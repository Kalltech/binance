import hmac
import hashlib
import logging
import requests
import time
import eventlet
from urllib.parse import urlencode


ENDPOINT = "https://www.binance.com"

BUY = "BUY"
SELL = "SELL"

LIMIT = "LIMIT"
MARKET = "MARKET"

GTC = "GTC"
IOC = "IOC"

options = {}


def set(apiKey, secret):
    """Set API key and secret.

    Must be called before any making any signed API calls.
    """
    options["apiKey"] = apiKey
    options["secret"] = secret


def get_ping():
    """Test request, returns []."""
    print("Fetching ping: ")
    r = request("GET", "/api/v1/ping", {})
    return r


def get_server_time():
    """Fetches the binance server time, equivalent to the time.time() result, measured in milliseconds"""
    r = request("GET", "/api/v1/time", {})
    return r["serverTime"]


def get_exchange_info():
    """Get latest exchange information."""
    print("Fetching exchange info: ")
    r = request("GET", "/api/v1/exchangeInfo", {})
    return r


def prices():
    """Get latest prices for all symbols."""
    data = request("GET", "/api/v3/ticker/price", {})
    return {d["symbol"]: d["price"] for d in data}


def tickers():
    """Get best price/qty on the order book for all symbols."""
    data = request("GET", "/api/v1/ticker/allBookTickers")
    return {d["symbol"]: {
        "bid": d["bidPrice"],
        "ask": d["askPrice"],
        "bidQty": d["bidQty"],
        "askQty": d["askQty"],
    } for d in data}


def depth(symbol, **kwargs):
    """Get order book.

    Args:
        symbol (str)
        limit (int, optional): Default 100. Must be one of 50, 20, 100, 500, 5,
            200, 10.

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = request("GET", "/api/v1/depth", params)
    return {
        "bids": {px: qty for px, qty, _ in data["bids"]},
        "asks": {px: qty for px, qty, _ in data["asks"]},
    }


def klines(symbol, interval, **kwargs):
    """Get kline/candlestick bars for a symbol.

    Klines are uniquely identified by their open time. If startTime and endTime
    are not sent, the most recent klines are returned.

    Args:
        symbol (str)
        interval (str)
        limit (int, optional): Default 500; max 1000.
        startTime (int, optional)
        endTime (int, optional)

    """
    params = {"symbol": symbol, "interval": interval}
    params.update(kwargs)
    data = request("GET", "/api/v1/klines", params)
    return [{
        "openTime": d[0],
        "open": d[1],
        "high": d[2],
        "low": d[3],
        "close": d[4],
        "volume": d[5],
        "closeTime": d[6],
        "quoteVolume": d[7],
        "numTrades": d[8],
    } for d in data]


def balances():
    """Get current balances for all symbols."""
    data = signedRequest("GET", "/api/v3/account", {})
    if 'msg' in data:
        raise ValueError("Error from exchange: {}".format(data['msg']))
    return {d["asset"]: {
        "free": d["free"],
        "locked": d["locked"],
    } for d in data.get("balances", [])}


def order(symbol, side, quantity, price, orderType=LIMIT, timeInForce=GTC,
          test=False, **kwargs):
    """Send in a new order.

    Args:
        symbol (str)
        side (str): BUY or SELL.
        quantity (float, str or decimal)
        price (float, str or decimal)
        orderType (str, optional): LIMIT or MARKET.
        timeInForce (str, optional): GTC or IOC.
        test (bool, optional): Creates and validates a new order but does not
            send it into the matching engine. Returns an empty dict if
            successful.
        newClientOrderId (str, optional): A unique id for the order.
            Automatically generated if not sent.
        stopPrice (float, str or decimal, optional): Used with stop orders.
        icebergQty (float, str or decimal, optional): Used with iceberg orders.

    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": orderType,
        "timeInForce": timeInForce,
        "quantity": formatNumber(quantity),
        "price": formatNumber(price),
    }
    params.update(kwargs)
    path = "/api/v3/order/test" if test else "/api/v3/order"
    data = signedRequest("POST", path, params)
    return data


def orderStatus(symbol, **kwargs):
    """Check an order's status.

    Args:
        symbol (str)
        orderId (int, optional)
        origClientOrderId (str, optional)
        recvWindow (int, optional)

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = signedRequest("GET", "/api/v3/order", params)
    return data


def cancel(symbol, **kwargs):
    """Cancel an active order.

    Args:
        symbol (str)
        orderId (int, optional)
        origClientOrderId (str, optional)
        newClientOrderId (str, optional): Used to uniquely identify this
            cancel. Automatically generated by default.
        recvWindow (int, optional)

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = signedRequest("DELETE", "/api/v3/order", params)
    return data


def openOrders(symbol, **kwargs):
    """Get all open orders on a symbol.

    Args:
        symbol (str)
        recvWindow (int, optional)

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = signedRequest("GET", "/api/v3/openOrders", params)
    return data


def allOrders(symbol, **kwargs):
    """Get all account orders; active, canceled, or filled.

    If orderId is set, it will get orders >= that orderId. Otherwise most
    recent orders are returned.

    Args:
        symbol (str)
        orderId (int, optional)
        limit (int, optional): Default 500; max 500.
        recvWindow (int, optional)

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = signedRequest("GET", "/api/v3/allOrders", params)
    return data


def myTrades(symbol, **kwargs):
    """Get trades for a specific account and symbol.

    Args:
        symbol (str)
        limit (int, optional): Default 500; max 500.
        fromId (int, optional): TradeId to fetch from. Default gets most recent
            trades.
        recvWindow (int, optional)

    """
    params = {"symbol": symbol}
    params.update(kwargs)
    data = signedRequest("GET", "/api/v3/myTrades", params)
    return data


def request(method, path, params=None):
    """Sends a request from the requests module

        If there is a TimeOut error or a bad request is sent (Status Code: 400),
        another request is sent and the previous ignored. When Binance responds with status code 200
        the data is processed.

        Args:
            method (str)
            path (str)

    """
    resp = None
    eventlet.monkey_patch()

    while not resp:
        with eventlet.Timeout(5, False):
            resp = requests.request(method, ENDPOINT + path, params=params)

        if not resp:
            print("Reattempting request: TimeOut")
        elif resp:
            if resp.status_code == 200:
                print("200 OK Request.")
            elif resp.status_code == 400:
                print("400 Bad Request:\nThe server cannot or will not process the request due"
                      " to an apparent client error (e.g., malformed request syntax, size too"
                      " large, invalid request message framing, or deceptive request routing).")
            else:
                print(resp)
        print()

    data = resp.json()
    if "msg" in data:
        logging.error(data['msg'])
    return data


def signedRequest(method, path, params):
    """Sends an api request from the requests module.

        If there is a TimeOut error or a bad request is sent (Status Code: 400),
        another request is sent and the previous ignored. When Binance responds with status code 200
        the data is processed.

        Args:
            method (str)
            path (str)

    """
    if "apiKey" not in options or "secret" not in options:
        raise ValueError("Api key and secret must be set")

    query = urlencode(sorted(params.items()))
    query += "&timestamp={}".format(int(time.time() * 1000))
    secret = bytes(options["secret"].encode("utf-8"))
    signature = hmac.new(secret, query.encode("utf-8"),
                         hashlib.sha256).hexdigest()
    query += "&signature={}".format(signature)

    resp = None
    eventlet.monkey_patch()

    while not resp:
        with eventlet.Timeout(5, False):
            resp = requests.request(method,
                                    ENDPOINT + path + "?" + query,
                                    headers={"X-MBX-APIKEY": options["apiKey"]})
        if resp is not None:
            if resp.status_code == 200:
                print("200 OK Request.")
            if resp.status_code == 400:
                print("400 Bad Request:\nThe server cannot or will not process the request due"
                      " to an apparent client error (e.g., malformed request syntax, size too"
                      " large, invalid request message framing, or deceptive request routing).")
        print()

    data = resp.json()
    if "code" in data:
        logging.error(data['code'])
    if "msg" in data:
        logging.error(data['msg'])
    return data


def formatNumber(x):
    if isinstance(x, float):
        return "{:.8f}".format(x)
    else:
        return str(x)