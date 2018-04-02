# _*_ coding: utf-8 _*_
from calendar import monthrange
from datetime import datetime, timedelta

import requests
from telebot import types

import config
import tokens
from utils.common_utils import TimeMemoize, bold, is_non_zero_file, my_bot
from utils.data_manager import my_data


class AcsManager:
    def __init__(self):
        self.acs_url = 'https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/index-text'
        self.in_url = 'https://corp.rfdyn.ru/index.php/site/now-in-office-text'
        self.in_office = set()
        self.in_office_old = set()

        self.asc_unaccessible_error = 'Сервер СКД сейчас недоступен :('

        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(types.InlineKeyboardButton(text="🔄", callback_data="in_office_update"))

    @staticmethod
    def time_format(time):
        return time.strftime('%Y-%m-%d')

    @staticmethod
    def reply_format(text, start_date, end_date):
        if is_non_zero_file(config.FileLocation.acs_answer):
            with open(config.FileLocation.acs_answer, 'r', encoding='utf-8') as file:
                split = text.split()
                nice = file.read()
                return nice.format(split[-5], split[-4], start_date, end_date, split[-2], split[-1])
        return text

    @staticmethod
    def state_format(text):
        if is_non_zero_file(config.FileLocation.acs_state_answer):
            with open(config.FileLocation.acs_state_answer, 'r', encoding='utf-8') as file:
                split = text.split()
                nice = file.read()
                if len(split) > 17:
                    return nice.format(split[-6], split[-5], 'В офисе' if split[18] == 'Вход' else 'Не в офисе',
                                       split[-2])
                return '🌴 Не в офисе сегодня 🌴'
        return text

    def year_time(self, message):
        today = datetime.today()
        year_start = today.replace(day=1, month=1)
        year_end = today.replace(day=31, month=12)
        self._make_time_request(message, year_start, year_end)

    def month_time(self, message):
        today = datetime.today()
        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])
        self._make_time_request(message, month_start, month_end)

    def week_time(self, message):
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        self._make_time_request(message, week_start, week_end)

    def day_time(self, message):
        today = datetime.today()
        self._make_time_request(message, today, today)

    def _make_time_request(self, message, start_date, end_date):
        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message.from_user.id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(start_date)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(end_date)),
                   ('AcsTabelIntermediadateSearch[summary_table]', '1'))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        answer = self.reply_format(response.text,
                                   self.time_format(start_date),
                                   self.time_format(end_date)) if response.ok else self.asc_unaccessible_error
        my_bot.reply_to(message, answer, parse_mode="HTML")

    def in_office_now_text(self, user_id=0):
        in_office_txt = self._make_in_office_request()
        for alert_user in my_data.data.get(str(user_id), {}).get('alert_users', []):
            in_office_txt = in_office_txt.replace(alert_user, bold(alert_user))
        return '👥 ' + in_office_txt

    def in_office_now(self, message):
        text = self.in_office_now_text(message.from_user.id)
        my_bot.reply_to(message, text, reply_markup=self.keyboard, parse_mode="HTML")

    def in_office_update(self, call):
        message = call.message
        text = self.in_office_now_text(message.chat.id)
        my_bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode="HTML")
        my_bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                         reply_markup=self.keyboard)
        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="✅  Данные обновлены")

    def in_office_alert(self):
        def need_alert():
            if my_data.get_user_settings(user_id)['alert_about_users'] == 'on':
                return True
            if my_data.get_user_settings(user_id)['alert_about_users'] == 'when_in_office':
                return self.is_user_in_office(user_id)

        self.in_office = set(self._make_in_office_request().split('\n'))
        if len(self.in_office) == 1:
            return
        if len(self.in_office_old) == 0:
            self.in_office_old = self.in_office
            return
        come = self.in_office - self.in_office_old
        gone = self.in_office_old - self.in_office

        for user_id, user in my_data.data.items():
            if need_alert():
                for alert_user in user.get('alert_users', []):
                    if alert_user in come:
                        my_bot.send_message(user_id, '👨🏻‍💻️ {} сейчас в офисе!'.format(alert_user))
                    if alert_user in gone:
                        my_bot.send_message(user_id, '🙇🏻 {} теперь не в офисе!'.format(alert_user))
        self.in_office_old = self.in_office

    def _make_in_office_request(self):
        response = requests.get(self.in_url, auth=(tokens.auth_login, tokens.auth_pswd))
        return response.text if response.ok else ''

    def user_state(self, message):
        today = datetime.today()

        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message.from_user.id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(today)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(today)))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        answer = self.state_format(response.text) if response.ok else self.asc_unaccessible_error
        my_bot.reply_to(message, answer, parse_mode="HTML")

    @TimeMemoize(delay=5 * 60 + 5)
    def is_user_in_office(self, user_id):
        today = datetime.today()

        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(user_id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(today)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(today)))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        if response.ok:
            split = response.text.split()
            if len(split) > 17:
                return split[18] == 'Вход'
        return True


my_acs = AcsManager()
