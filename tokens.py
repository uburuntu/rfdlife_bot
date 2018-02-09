# _*_ coding: utf-8 _*_

import os

# Set your api tokens and keys manually or through environmental variables
# (add lines to your .bashrc and restart terminal):
# export BOT_TELEGRAM_TOKEN="XXXXX:XXXXXXXXXXX"

default_bot = ""
bot = os.getenv('RFDLIFE_BOT_TELEGRAM_TOKEN', default_bot)
