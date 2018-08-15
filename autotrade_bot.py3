#!/usr/bin/env python
import time
from telethon import TelegramClient, events
import configparser
#from telethon.tl.types import PeerUser, PeerChat, PeerChannel
#pip3 install typing
#pip3 install telethon
#pip3 install configparser
#Create an app in https://my.telegram.org/apps and put info in INI

# sample API_ID from https://github.com/telegramdesktop/tdesktop/blob/f98fdeab3fb2ba6f55daf8481595f879729d1b84/Telegram/SourceFiles/config.h#L220

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
api_username = ConfigSectionMap("BINANCE_API", load_params)['my_telegram_app_api_username']
bot_name= ConfigSectionMap("BINANCE_API", load_params)['my_telegram_bot_name']
telegram_chat= ConfigSectionMap("BINANCE_API", load_params)['telegram_chat']
auto_trade= ConfigSectionMap("BINANCE_API", load_params)['auto_trade']

def main():
    # Create the client and connect
    client = TelegramClient(api_username, api_id, api_hash, update_workers=1, spawn_read_thread=False)
    client.start()

    @client.on(events.NewMessage(incoming=True))
    def _(event):
        print("\nevent")
        load_params.read("binance_api.ini")
        bot_name= ConfigSectionMap("BINANCE_API", load_params)['my_telegram_bot_name']
        telegram_chat= ConfigSectionMap("BINANCE_API", load_params)['telegram_chat']
        auto_trade= ConfigSectionMap("BINANCE_API", load_params)['auto_trade']
#        print(event.message)
#        print(event.message.from_id)
#        print(event.message.message.lower())
        print(str(event.message.to_id))
#        ch_id=client.get_entity(PeerChannel(event.message.to_id))
#        print(ch_id)
        if auto_trade=="1":
            print("autotrade:on")
            if ("buy:" in event.message.message.lower() or "buybelow:" in event.message.message.lower()) and str(event.message.to_id)==telegram_chat:
#            if ("buy:" in event.message.message.lower() or "buybelow:" in event.message.message.lower()):
                print("Envoi\n"+event.message.message)
                client.send_message(bot_name, event.message.message)
                time.sleep(1)  # pause for 1 second to rate-limit automatic replies
        else:
            print("auto_trade disabled\n"+event.message.message)

    print(time.asctime(), '-', "Starting autotrade")
    print(str(api_id)+"/"+api_hash+"/"+bot_name+"/"+telegram_chat)
    if auto_trade=="1": print("autotrade:on")
    client.idle()
    client.disconnect()
    print(time.asctime(), '-', 'Stopped!')


if __name__ == '__main__':
    main()
