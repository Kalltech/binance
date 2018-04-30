#!/usr/bin/env python
############################################
#Create an app in https://my.telegram.org/apps and put info in INI

from telethon import TelegramClient, events
import configparser
load_params = configparser.ConfigParser()
load_params.read("binance_api.ini")

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
bot_name= ConfigSectionMap("BINANCE_API", load_params)['my_telegram_bot_name']
telegram_chat= ConfigSectionMap("BINANCE_API", load_params)['telegram_chat']

print(str(api_id)+"/"+api_hash+"/"+bot_name+"/"+telegram_chat)

client = TelegramClient('session_telethon', api_id, api_hash, update_workers=1, spawn_read_thread=False)
client.start()
print("Starting autotrade")
@client.on(events.NewMessage(incoming=True,chats=telegram_chat))
def my_event_handler(event):
    print(event.raw_text)
    if "buy:" in event.raw_text.lower():
        print("Envoi\n"+event.raw_text)
        client.send_message(bot_name, event.raw_text)
client.idle()
