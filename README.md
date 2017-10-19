# Binance API client in Python

#### Features
- Does not require an api key for public methods
- Code is concise and clean
- Compatible with Python 2.7-3.6

#### Installation
```
pip install binance
```

#### Usage
```
import binance
```

For authenticated API calls, set your API key and secret
```
binance.set("your api key", "your secret key")
```

#### Get prices for all symbols
```
binance.prices()
```

#### Get tickers for all symbols
```
binance.tickers()
```

#### Get order book
```
binance.depth("BNBBTC")
binance.depth("BNBBTC", limit=5)  # top 5 levels only
```

#### Get klines
```
binance.klines("BNBBTC", "1m")
```

#### Get balances for all currencies
```
binance.balances()
```

#### Place order
```
# place 1000 lot buy order at 0.000001 on BNBBTC
binance.order("BNBBTC", binance.BUY, 1000, 0.000001)

# test an order to see if any errors are returned from the API
binance.order("BNBBTC", binance.BUY, 1000, 0.000001, test=True)

# use a client id to identify the order later
binance.order("BNBBTC", binance.BUY, 1000, 0.000001, newClientOrderId="foobar")
```

#### Cancel order
```
binance.cancel("BNBBTC", orderId=12345678)  # by order id
binance.cancel("BNBBTC", origClientOrderId="foobar")  # by client id
```

#### Get order status
```
binance.orderStatus("BNBBTC", orderId=12345678)  # by order id
binance.orderStatus("BNBBTC", origClientOrderId="foobar")  # by client id
```

#### Get all open orders
```
binance.openOrders("BNBBTC")
```

#### Get open and closed orders
```
binance.allOrders("BNBBTC")
```

#### Get trades
```
binance.myTrades("BNBBTC")
```
