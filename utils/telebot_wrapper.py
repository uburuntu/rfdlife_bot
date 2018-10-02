import functools
from datetime import datetime
from itertools import cycle
from urllib.parse import unquote

import requests
import telebot
from telebot import apihelper
from telebot.apihelper import ApiException, _get_req_session


def retry(exception, retries_count=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            ret, exc = None, None
            for _ in range(retries_count):
                try:
                    ret = func(*args, **kwargs)
                except exception as e:
                    exc = e
                else:
                    break
                TelebotWrapper.set_proxy()
            else:
                TelebotWrapper.log_exception(exc)
            return ret

        return wrapped

    return decorator


class TelebotWrapper(telebot.TeleBot):
    # Free Telegram proxies from t.me/proxyme and others
    proxies_list = [
        'socks5://telegram:telegram@sr123.spry.fail:1080',
        'socks5://telegram:telegram@k45i6.nimble.zone:1080',
        'socks5://telegram:telegram@239h4ym.spry.wtf:1080',
        'socks5://28006241:F1zcUqql@phobos.public.opennetwork.cc:1090',
        'socks5://28006241:F1zcUqql@deimos.public.opennetwork.cc:1090',
        'socks5://telegram:telegram@sreju5h4.spry.fail:1080',
        'socks5://telegram:telegram@rmpufgh1.teletype.live:1080',
        'socks5://user_2JpM:uwJeUn7jHMUdtinF@s2.shadowsocks.wtf:6685',
        'socks5://antimalware:eL2S5JbU@148.251.151.141:1080',
    ]
    curr_proxy = cycle(proxies_list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ''

        apihelper.CONNECT_TIMEOUT = 2.5

    def init_name(self):
        self.name = '@' + self.get_me().username

    @staticmethod
    def set_proxy():
        apihelper.proxy = {'https': next(TelebotWrapper.curr_proxy)}
        _get_req_session(reset=True)

    @staticmethod
    def log_exception(exc):
        def log(text):
            curr_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            print('{}\n{}\n'.format(curr_time, text))

        if isinstance(exc, ApiException):
            log('Telegram api exception: function {}; result {};'.format(exc.function_name, exc.result))
        elif isinstance(exc, requests.exceptions.ConnectionError):
            log('Telegram connection exception at: {}'.format(unquote(exc.request.path_url).split('/')[-1]))
        else:
            log('Exception: {};'.format(str(exc)))

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
