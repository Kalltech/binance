#!/usr/bin/env python
import time
from telethon import TelegramClient, events,  utils
import configparser
import sys,  os
import pickle
sys.path.append("/usr/local/lib/python2.7/dist-packages")
import string
import ast
import json
from influxdb import InfluxDBClient
import datetime

#from telethon.tl.types import PeerUser, PeerChat, PeerChannel
#pip3 install typing
#pip3 install telethon
#pip3 install configparser
#Create an app in https://my.telegram.org/apps and put info in INI

# sample API_ID from https://github.com/telegramdesktop/tdesktop/blob/f98fdeab3fb2ba6f55daf8481595f879729d1b84/Telegram/SourceFiles/config.h#L220

load_params = configparser.ConfigParser()
load_params.read("binance_api.ini")
T1 = []
T2 = []
T3 = []
T1_global = []
T2_global = []
T3_global = []

if os.path.exists("T1")==True:
    with open("T1", 'rb') as f:
        T1=pickle.load(f)
        print(str(T1))
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
def ConfigSectionMap(section, Config):
  dict1 = {}
  options = Config.options(section)
  for option in options:    
    try:
      dict1[option] = Config.get(section, option)
      if dict1[option] == -1:
         print("skip: %s" % option)
    except:
      print("exception on %s!" % option)
      dict1[option] = None
  return dict1

api_id = ConfigSectionMap("BINANCE_API", load_params)['my_telegram_app_api_id']
api_hash = ConfigSectionMap("BINANCE_API", load_params)['my_telegram_app_api_hash']
api_username = ConfigSectionMap("BINANCE_API", load_params)['my_telegram_app_api_username']
api_number = ConfigSectionMap("BINANCE_API", load_params)['my_telegram_app_api_number']
bot_name= ConfigSectionMap("BINANCE_API", load_params)['my_telegram_bot_name']
telegram_chat= ConfigSectionMap("BINANCE_API", load_params)['telegram_chat']
influxdb_user= ConfigSectionMap("BINANCE_API", load_params)['influxdb_user']
influxdb_password= ConfigSectionMap("BINANCE_API", load_params)['influxdb_password']
influxdb_dbname= ConfigSectionMap("BINANCE_API", load_params)['influxdb_dbname']
influxdb_dbuser= ConfigSectionMap("BINANCE_API", load_params)['influxdb_dbuser']
influxdb_dbuser_password= ConfigSectionMap("BINANCE_API", load_params)['influxdb_dbuser_password']
influxdb_host= ConfigSectionMap("BINANCE_API", load_params)['influxdb_host']
influxdb_port= ConfigSectionMap("BINANCE_API", load_params)['influxdb_port']
influxdb_enabled= ConfigSectionMap("BINANCE_API", load_params)['influxdb_enabled']
telegram_chat_list = ast.literal_eval(load_params.get('BINANCE_API', 'telegram_chat_list'))
#auto_trade= ConfigSectionMap("BINANCE_API", load_params)['auto_trade']

def load_obj(name ):
    with open(name) as json_data:
        dct_load_obj = json.load(json_data)
        json_data.close()
        return dct_load_obj

def to_db(COIN="XXX",  TX="TX", TX_nb="0"):
    """Instantiate a connection to the InfluxDB."""
    user = influxdb_user
    password = influxdb_password
    dbname = influxdb_dbname
    dbuser = influxdb_dbuser
    dbuser_password = influxdb_dbuser_password
    host=influxdb_host
    port=influxdb_port
#    query = 'select value from cpu_load_short;'
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

    client = InfluxDBClient(host, port, user, password, dbname)
    client2 = InfluxDBClient(host, port, user, password, "binance_balance")

#    print("Create database: " + dbname)
    client.create_database(dbname)
    client2.create_database("binance_balance")

#    print("Create a retention policy")
#    client.create_retention_policy('awesome_policy', '3d', 3, default=True)

#    print("Switch user: " + dbuser)
    client.switch_user(dbuser, dbuser_password)
    client2.switch_user(dbuser, dbuser_password)

    print("Write points: {0}".format(json_body))
    client.write_points(json_body)
    client2.write_points(json_body2)
    client2.write_points(json_body3)

#    print("Querying data: " + query)
#    result = client.query(query)
#
#    print("Result: {0}".format(result))

#    print("Switch user: " + user)
#    client.switch_user(user, password)

#    print("Drop database: " + dbname)
#    client.drop_database(dbname)
#                T3 = count_T(T3, COIN, TX)

def count_T(count_T_TX, count_T_COIN,  count_T_Name):
    x_count = 0
    new_TX = []
    for x in count_T_TX:
        diff_time=datetime.datetime.now()-x
#        print(diff_time.total_seconds())
        if int(diff_time.total_seconds()) < 60:
            x_count = x_count + 1
            new_TX.append(x)
#    print(x_count)
#    print(count_T_COIN+"/"+count_T_Name+"/"+str(x_count))
    if "global" in count_T_COIN: count_T_COIN="T_global"
    to_db(count_T_COIN, count_T_Name, x_count)
    with open(count_T_Name, 'wb') as f:
        pickle.dump(count_T_TX, f, pickle.HIGHEST_PROTOCOL)
    return new_TX


def main():
    # Create the client and connect
    client = TelegramClient(api_username, api_id, api_hash, update_workers=1, spawn_read_thread=False)
    client.start(api_number)
#    lonami = client.get_entity('lonami')
#    print(lonami)
#    print(type(lonami))
#    print(utils.get_display_name(lonami))

    @client.on(events.NewMessage(incoming=True))
    def _(event):
        print("*********************************************************")
        global T1
        global T2
        global T3
        global T1_global
        global T2_global
        global T3_global
        load_params.read("binance_api.ini")
        bot_name= ConfigSectionMap("BINANCE_API", load_params)['my_telegram_bot_name']
#        telegram_chat= ConfigSectionMap("BINANCE_API", load_params)['telegram_chat']
#        a_telegram_chat = telegram_chat.split(",")
        influxdb_collectors= ConfigSectionMap("BINANCE_API", load_params)['influxdb_collectors']
        a_influxdb_collectors = influxdb_collectors.split(",")
#        auto_trade= ConfigSectionMap("BINANCE_API", load_params)['auto_trade']
        telegram_chat_list = ast.literal_eval(load_params.get('BINANCE_API', 'telegram_chat_list'))
        from_id=""
        to_id=""
#        print(event)
        print(str(datetime.datetime.now()))
        if event.message.from_id is not None:
            try:
                entity=client.get_entity(event.message.from_id)
                from_id=utils.get_display_name(entity)
                print("From:"+from_id+":"+str(event.message.from_id))
            except: 
                pass
        if event.message.to_id is not None:
            try:
                entity=client.get_entity(event.message.to_id)
                to_id=utils.get_display_name(entity)
                print("To:"+to_id+":"+str(event.message.to_id))
            except: 
                pass
        printable = set(string.printable)
#        print(event.message.message.lower()[:35])
        if not "PeerChannel(channel_id=1228970642)" in str(event.message.to_id) and not "PeerChannel(channel_id=1244535252)" in str(event.message.to_id) and not "PeerChannel(channel_id=1363803244)" in str(event.message.to_id) :
            text_sent="".join(list(filter(lambda x: x in printable, event.message.message.lower())))
            print(text_sent[:35])
    #        ch_id=client.get_entity(PeerChannel(event.message.to_id))
    #        print(ch_id)
#            if auto_trade=="1":
#                print("autotrade_enabled")
            for tgm_ct, u  in telegram_chat_list.items():
#                print(tgm_ct+"/"+u)
                if tgm_ct in str(event.message.to_id) and not from_id=="Kalltech_Api_Bot":
                    if ("entry zone:" in text_sent or "buy:" in text_sent or "buy :" in text_sent or "buy below:" in text_sent or "buy above or in:" in text_sent or "buy below or in:" in text_sent or "buy below or close to:" in text_sent):
    #                if ("buy:" in text_sent or "buy below:" in text_sent):
                        print("Envoi")
    #                    text_sent="".join(list(filter(lambda x: x in printable, event.message.message)))
                        print(str(event.message.to_id)+":"+to_id+"\n"+text_sent+"\nUSD:"+str(u))
                        client.send_message(bot_name, str(event.message.to_id)+":"+to_id+"\n"+text_sent+"\nUSD:"+str(u))
                        time.sleep(1)  # pause for 1 second to rate-limit automatic replies
                        client.send_message("Signals_All", str(event.message.to_id)+":"+to_id+"\n"+text_sent)
#            else:
#                print("auto_trade disabled\n")
            for collectors in a_influxdb_collectors:
                if influxdb_enabled == "1" and"target" in text_sent and collectors in str(event.message.to_id):
                    print("influxdb_enabled")
        #        if "target" in text_sent:
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

    print(time.asctime(), '-', "Starting autotrade")
#    print(str(api_id)+"/"+api_hash+"/"+bot_name+"/"+telegram_chat)
#    if auto_trade=="1": print("autotrade_enabled")
    client.idle()
    client.disconnect()
    print(time.asctime(), '-', 'Stopped!')


if __name__ == '__main__':
    main()
