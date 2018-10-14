#!/usr/bin/env python
import time
from telethon import TelegramClient, events,  utils
import sys,  os
import pickle
sys.path.append("/usr/local/lib/python2.7/dist-packages")
import string
import json
from influxdb import InfluxDBClient
import datetime

json_ini="api4.json"

T1 = []
T2 = []
T3 = []
T1_global = []
T2_global = []
T3_global = []

if os.path.exists("T1")==True:
    with open("T1", 'rb') as f:
        T1=pickle.load(f)
if os.path.exists("T2")==True:
    with open("T2", 'rb') as f:
        T2=pickle.load(f)
if os.path.exists("T3")==True:
    with open("T3", 'rb') as f:
        T3=pickle.load(f)
if os.path.exists("T1_global")==True:
    with open("T1_global", 'rb') as f:
        T_global=pickle.load(f)
if os.path.exists("T2_global")==True:
    with open("T2_global", 'rb') as f:
        T_global=pickle.load(f)
if os.path.exists("T3_global")==True:
    with open("T3_global", 'rb') as f:
        T_global=pickle.load(f)
        
def load_obj(name ):
    with open(name) as json_data:
        dct_load_obj = json.load(json_data)
        json_data.close()
        return dct_load_obj

def save_obj(obj, name ):
    save_obj_out_file = open(name,"w")
    json.dump(obj,save_obj_out_file, indent=4, sort_keys=True)                                    
    save_obj_out_file.close()

def to_db_balances():
    user = dct_INI_JSON['str_influxdb_user']
    password = dct_INI_JSON['str_influxdb_password']
    dbname = "binance_balance"
    dbuser = dct_INI_JSON['str_influxdb_dbuser']
    dbuser_password = dct_INI_JSON['str_influxdb_password']
    host=dct_INI_JSON['str_influxdb_host']
    port=dct_INI_JSON['str_influxdb_port']
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    client2 = InfluxDBClient(host, port, user, password, dbname)
    client2.create_database(dbname)
    client2.switch_user(dbuser, dbuser_password)

    binance_usd=load_obj("./temp/binance_usd")
    bitmex_usd=load_obj("./temp/bitmex_usd")
    json_body2 = [
        {
            "measurement": "Binance_Stats",
            "tags": {
                "BINANCE": "BINANCE",
            },
            "time": current_time,
            "fields": {
                "total_usd": binance_usd['total_usd'],
                "total_btc": binance_usd['total_btc'],
            }
        }
    ]
    json_body3 = [
        {
            "measurement": "Binance_Stats",
            "tags": {
                "BINANCE": "BINANCE",
            },
            "time": current_time,
            "fields": {
                "total_usd_bitmex": bitmex_usd['total_usd'],
                "total_btc_bitmex": bitmex_usd['total_btc'],
            }
        }
    ]
    print("Write points: {0}".format(json_body2))
    print("Write points: {0}".format(json_body3))
    client2.write_points(json_body2)
    client2.write_points(json_body3)
    
def to_db(COIN="XXX",  TX="TX", TX_nb="0"):
    """Instantiate a connection to the InfluxDB."""
    user = dct_INI_JSON['str_influxdb_user']
    password = dct_INI_JSON['str_influxdb_password']
    dbname = dct_INI_JSON['str_influxdb_dbname']
    dbuser = dct_INI_JSON['str_influxdb_dbuser']
    dbuser_password = dct_INI_JSON['str_influxdb_password']
    host=dct_INI_JSON['str_influxdb_host']
    port=dct_INI_JSON['str_influxdb_port']
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [
        {
            "measurement": "SP_Stats",
            "tags": {
                "COIN": COIN,
            },
            "time": current_time,
            "fields": {
                TX: TX_nb,
            }
        }
    ]
    client = InfluxDBClient(host, port, user, password, dbname)
    client.create_database(dbname)
    client.switch_user(dbuser, dbuser_password)
    print("Write points: {0}".format(json_body))
    client.write_points(json_body)

def count_T(count_T_TX, count_T_COIN,  count_T_Name):
    x_count = 0
    new_TX = []
    for x in count_T_TX:
        diff_time=datetime.datetime.now()-x
        if int(diff_time.total_seconds()) < 60:
            x_count = x_count + 1
            new_TX.append(x)
    if "global" in count_T_COIN: count_T_COIN="T_global"
    to_db(count_T_COIN, count_T_Name, x_count)
    with open(count_T_Name, 'wb') as f:
        pickle.dump(count_T_TX, f, pickle.HIGHEST_PROTOCOL)
    return new_TX


def main():
    # Create the client and connect
    client = TelegramClient(dct_INI_JSON['str_my_telegram_app_api_username'], dct_INI_JSON['str_my_telegram_app_api_id'], dct_INI_JSON['str_my_telegram_app_api_hash'], update_workers=1, spawn_read_thread=False)
    client.start(dct_INI_JSON['str_my_telegram_app_api_number'])

    @client.on(events.NewMessage(incoming=True))
    def _(event):
        print("*********************************************************")
        global T1
        global T2
        global T3
        global T1_global
        global T2_global
        global T3_global
        dct_INI_JSON=load_obj(json_ini)
        from_id=""
        to_id=""
#        print(event)
        id_vs_displayname = {}
        if os.path.exists("id_vs_displayname.json")==True:
            id_vs_displayname=load_obj("./id_vs_displayname.json")
        print(str(datetime.datetime.now()))
        if event.message.from_id is not None:
            try:
                entity=client.get_entity(event.message.from_id)
                from_id=utils.get_display_name(entity)
                print("From:"+from_id+":"+str(event.message.from_id))
                id_vs_displayname[str(event.message.from_id)] = from_id
            except: 
                pass
        if event.message.to_id is not None:
            try:
                entity=client.get_entity(event.message.to_id)
                to_id=utils.get_display_name(entity)
                print("To:"+to_id+":"+str(event.message.to_id))
                id_vs_displayname[str(event.message.to_id)] = to_id
            except: 
                pass
        save_obj(id_vs_displayname, "./id_vs_displayname.json")
        printable = set(string.printable)
        if not str(event.message.to_id).lower() in str(dct_INI_JSON['list_blacklist_signals_all']).lower():
            text_sent="".join(list(filter(lambda x: x in printable, event.message.message.lower())))
            print(text_sent[:35])
            if str(event.message.to_id).lower() in str(dct_INI_JSON['list_whitelist_signals_all']).lower():
                if ("entry zone:" in text_sent or "buy under " in text_sent or "buy zone " in text_sent\
                or "tca " in text_sent or "open at" in text_sent or "accumulate between" in text_sent\
                or "buy:" in text_sent or "buy :" in text_sent or "buy below:" in text_sent\
                or "buy above or in:" in text_sent or "buy below or in:" in text_sent\
                or ("target 1 " in text_sent and not "touched" in text_sent)\
                or ("target 1 " in text_sent and not "reached" in text_sent)\
                or "buy below or close to:" in text_sent):
                    if str(event.message.to_id).lower()==str("PeerChannel(channel_id=1322719136)").lower():
                        
                        print("Envoi Bot")
                        client.send_message(dct_INI_JSON['str_my_telegram_bot_name'],text_sent)
                        time.sleep(1)  # pause for 1 second to rate-limit automatic replies
                    else:
                        print("Envoi Bot & Signals_All")
                        print("CHNL:"+str(event.message.to_id)+":"+to_id+"\nBot:"+dct_INI_JSON['str_my_telegram_bot_name']+"\n"+text_sent)
                        client.send_message(dct_INI_JSON['str_my_telegram_bot_name'],\
                        "CHNL:"+str(event.message.to_id)+":"+to_id+"\nBot:"+dct_INI_JSON['str_my_telegram_bot_name']+"\n"+text_sent)
                        time.sleep(1)  # pause for 1 second to rate-limit automatic replies
                        client.send_message("Signals_All",\
                        "CHNL:"+str(event.message.to_id)+":"+to_id+"\nBot:"+dct_INI_JSON['str_my_telegram_bot_name']+"\n"+text_sent)
            else:
                print("Not on whitelist")
            if dct_INI_JSON['bool_influxdb_enabled']:
                print("bool_influxdb_enabled")
                to_db_balances()
                for collectors in dct_INI_JSON['list_influxdb_collectors'].split(","):
                        if "target" in text_sent and collectors in str(event.message.to_id):
                            current_time = datetime.datetime.now()
                            COIN=text_sent.split(" touched")[0]
                            if "target 1" in text_sent:
                                TX="T1"
                                T1.append(current_time)
                                T1 = count_T(T1, COIN, TX)
                                T1_global.append(current_time)
                                T1_global = count_T(T1_global, "T1_global", "T1_global")
                            if "target 2" in text_sent:
                                TX="T2"
                                T2.append(current_time)
                                T2 = count_T(T2, COIN, TX)
                                T2_global.append(current_time)
                                T2_global = count_T(T2_global, "T2_global", "T2_global")
                            if "target 3" in text_sent:
                                TX="T3"
                                T3.append(current_time)
                                T3 = count_T(T3, COIN, TX)
                                T3_global.append(current_time)
                                T3_global = count_T(T3_global, "T3_global", "T3_global")
        else:
            print("On blacklist")
            
    print("Starting autotrade")
    client.idle()
    client.disconnect()
    print(time.asctime(), '-', 'Stopped!')

dct_INI_JSON=load_obj(json_ini)
if __name__ == '__main__':
    main()
