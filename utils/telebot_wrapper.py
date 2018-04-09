# _*_ coding: utf-8 _*_
from datetime import datetime

import telebot
from telebot.apihelper import ApiException


class TelebotWrapper(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def log(text):
        print("Telegram api exception: {}\n{}\n".format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), text))

    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None):
        try:
            super().send_message(chat_id, text, disable_web_page_preview, reply_to_message_id, reply_markup,
                                 parse_mode, disable_notification)
        except ApiException as e:
            self.log(f"{e},\nchat_id={chat_id}, text=({text})")
