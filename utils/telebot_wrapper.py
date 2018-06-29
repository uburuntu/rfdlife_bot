# _*_ coding: utf-8 _*_
from datetime import datetime

import functools
import telebot
from telebot.apihelper import ApiException


def retry(exception, retries_count=2):
    def my_decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            ret, exc = None, None
            for attempt in range(retries_count):
                try:
                    ret = func(*args, **kwargs)
                except exception as e:
                    exc = e
                else:
                    break
            else:
                TelebotWrapper.log(f'function {func.__name__}; {exc}')
            return ret

        return wrapped

    return my_decorator


class TelebotWrapper(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ''

    @staticmethod
    def log(text):
        print('{}\nTelegram api exception: {}\n'.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'), text))

    def init_name(self):
        self.name = '@' + self.get_me().username

    @retry(ApiException)
    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None):
        return super().send_message(chat_id, text, disable_web_page_preview, reply_to_message_id, reply_markup,
                                    parse_mode, disable_notification)

    @retry(ApiException)
    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None, parse_mode=None,
                          disable_web_page_preview=None, reply_markup=None):
        return super().edit_message_text(text, chat_id, message_id, inline_message_id, parse_mode,
                                         disable_web_page_preview, reply_markup)
