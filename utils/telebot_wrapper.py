import functools
from datetime import datetime

import requests
import telebot
from telebot.apihelper import ApiException


def retry(exception, retries_count=5):
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
                TelebotWrapper.log_exception(exc, *args, **kwargs)
            return ret

        return wrapped

    return my_decorator


class TelebotWrapper(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ''

    def init_name(self):
        self.name = '@' + self.get_me().username

    @staticmethod
    def log_exception(exc, *args, **kwargs):
        def log(text):
            curr_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            print('{}\n{}\n'.format(curr_time, text))

        if isinstance(exc, ApiException):
            log('Telegram api exception: function {}; result {};'.format(exc.function_name, exc.result))
        elif isinstance(exc, requests.exceptions.ConnectionError):
            log('Telegram connection exception: {:.100};'.format(str(exc)))
        else:
            log('Exception: {};'.format(exc))

    @retry((ApiException, requests.exceptions.ConnectionError))
    def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None,
                     parse_mode=None, disable_notification=None):
        return super().send_message(chat_id, text, disable_web_page_preview, reply_to_message_id, reply_markup,
                                    parse_mode, disable_notification)

    @retry((ApiException, requests.exceptions.ConnectionError))
    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None, parse_mode=None,
                          disable_web_page_preview=None, reply_markup=None):
        return super().edit_message_text(text, chat_id, message_id, inline_message_id, parse_mode,
                                         disable_web_page_preview, reply_markup)
