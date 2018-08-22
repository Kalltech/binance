#Kallmod

# Simple Binance API client in Python with signals

Create your bot, modify ini, update binance.py in /usr/local/lib/python2.7/dist-packages/binance.py

Launch python2 telegram_bot_binance.py2
Launch python2 watchdog_binance.py2
Launch python3 autotrade_bot.py3
Or Launch run_all.sh


From your telegram send signal XLMBTC etc... or status to the bot

- Does not require an api key for public methods
- Some compatible with Python 2.7, some not...

apt-get install python-requests

apt-get install python-pip

pip install python-telegram-bot --upgrade

pip install binance

Python3:

import time, configparser, sys,  os, pickle

from telethon import TelegramClient, events
 
Python2:

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from telegram import ReplyKeyboardMarkup,  InlineKeyboardMarkup,  InlineKeyboardButton

import logging, os, datetime, string, json, glob, inotify.adapters, psutil, ConfigParser, progressbar, time, sys, binance, requests, pickle, math, telegram, shutil, ntpath
