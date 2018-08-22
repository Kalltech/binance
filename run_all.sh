#!/bin/sh
# Run all necessary scripts!
echo Run all

#python2 binance3.py2 &
python3 autotrade_bot.py3 &
python2 telegram_bot_binance.py2 &
python2 watchdog_binance.py2
