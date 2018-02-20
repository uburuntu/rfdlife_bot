# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import json
from calendar import monthrange
from datetime import datetime, timedelta

import requests

import config
import tokens
from utils import global_lock, my_bot, is_non_zero_file, bold, user_action_log


class DataManager:
    def __init__(self, file_name=config.file_location['user_data']):
        self.file_name = file_name
        self.data = dict()
        self.load()

    def load(self):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
            global_lock.release()

    def save(self):
        global_lock.acquire()
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=True)
        global_lock.release()

    def dump_file(self, message):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                my_bot.reply_to(message, file.read())
            global_lock.release()

    def command_need_name(self, func):
        def wrapped(message):
            if not self.is_registered(message) or not self.is_name_set(message):
                user_action_log(message, "not registered to call: " + message.text)
                self.register_user(message)
                return
            return func(message)

        return wrapped

    def is_registered(self, message):
        if self.data.get(str(message.from_user.id)) is not None:
            if self.data.get(str(message.from_user.id)).get('authenticated', 'False') == 'True':
                return True
        return False

    def is_name_set(self, message):
        if self.data.get(str(message.from_user.id)) is not None:
            if self.data.get(str(message.from_user.id)).get('name') is not None:
                return True
        return False

    def register_user(self, message):
        if not self.is_registered(message):
            sent = my_bot.send_message(message.from_user.id,
                                       bold('Авторизация') + '\n\nВведи пароль:', parse_mode="HTML")
            my_bot.register_next_step_handler(sent, self.check_password)
            return

        sent = my_bot.send_message(message.from_user.id, 'Твой номер в СКД? Например: 5059, 5060 и т.д.')
        my_bot.register_next_step_handler(sent, self.set_user_name)

    def check_password(self, message):
        if tokens.access_pswd != "" and message.text == tokens.access_pswd:
            if self.data.get(str(message.from_user.id)) is None:
                self.data[str(message.from_user.id)] = {"authenticated": "True"}
            else:
                self.data[str(message.from_user.id)]["authenticated"] = "True"
            user_action_log(message, "successfully registered")
            my_bot.reply_to(message, "✅ Пароль верный!")
            self.register_user(message)
        else:
            user_action_log(message, "entered wrong password")
            my_bot.reply_to(message, "⛔ Пароль не подошел!")

    def set_user_name(self, message):
        # Todo: check existing
        if message.text.isdigit():
            self.data[str(message.from_user.id)]['name'] = str(message.text)
            self.register_user_finish(message)
        else:
            my_bot.send_message(message.from_user.id, 'Ошибка, нужно указать номер')

    def register_user_finish(self, message):
        self.save()
        my_bot.send_message(message.from_user.id, 'Теперь можете использовать /week и т.п.\n'
                                                  'Для смены пользователя вызывайте /restart.')

    def get_user_name(self, message):
        if self.is_name_set(message):
            return self.data.get(str(message.from_user.id), {}).get('name', '5059')
        else:
            my_bot.reply_to(message, 'Вы не авторизованы! Используйте /restart')

    def add_alert_name(self, message):
        split = message.text.split(' ', 1)
        if len(split) > 1:
            if self.data[str(message.from_user.id)].get('alert_users') is not None:
                if self.data[str(message.from_user.id)]['alert_users'].count(split[1]) == 0:
                    self.data[str(message.from_user.id)]['alert_users'].append(split[1])
            else:
                self.data[str(message.from_user.id)]['alert_users'] = [split[1]]
            self.save()
            my_bot.reply_to(message, '⚙️ Оповещения о {} включены!'.format(split[1]))
        else:
            my_bot.reply_to(message, 'Использование: /alert_add <ФИО из /in_office>')

    def erase_alert_name(self, message):
        split = message.text.split(' ', 1)
        if len(split) > 1:
            if self.data[str(message.from_user.id)].get('alert_users') is not None:
                if self.data[str(message.from_user.id)]['alert_users'].count(split[1]) != 0:
                    self.data[str(message.from_user.id)]['alert_users'].remove(split[1])
                    self.save()
                    my_bot.reply_to(message, '⚙️ Оповещения о {} выключены!'.format(split[1]))
                    return
        my_bot.reply_to(message, 'Использование: /alert_erase <ФИО из /in_office>')

    def list_alert_name(self, message):
        users = self.data[str(message.from_user.id)].get('alert_users')
        if users is not None and len(users) > 0:
            my_bot.reply_to(message, '⚙️ Ваш список оповещений:\n— {}\n\n'
                                     'Используйте /alert_add и /alert_erase для управления списком.'
                                     ''.format('\n— '.join(self.data[str(message.from_user.id)].get('alert_users'))))
        else:
            my_bot.reply_to(message, '⚙️ Ваш список оповещений пуст.\n\n'
                                     'Используйте /alert_add и /alert_erase для управления списком.')


class AcsManager:
    def __init__(self):
        self.acs_url = 'https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/index-text'
        self.in_url = 'https://corp.rfdyn.ru/index.php/site/now-in-office-text'
        self.in_office = set()
        self.in_office_old = set()

    @staticmethod
    def time_format(time):
        return time.strftime('%Y-%m-%d')

    @staticmethod
    def reply_format(text, start_date, end_date):
        if is_non_zero_file(config.file_location['acs_answer']):
            with open(config.file_location['acs_answer'], 'r', encoding='utf-8') as file:
                split = text.split()
                nice = file.read()
                return nice.format(split[-5], split[-4], start_date, end_date, split[-2], split[-1])
        return text

    @staticmethod
    def state_format(text):
        if is_non_zero_file(config.file_location['acs_state_answer']):
            with open(config.file_location['acs_state_answer'], 'r', encoding='utf-8') as file:
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
        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(start_date)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(end_date)),
                   ('AcsTabelIntermediadateSearch[summary_table]', '1'))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        my_bot.reply_to(message, self.reply_format(response.text,
                                                   self.time_format(start_date), self.time_format(end_date)),
                        parse_mode="HTML")

    def in_office_now(self, message):
        my_bot.reply_to(message, '👥 ' + self._make_in_office_request())

    def in_office_alert(self):
        self.in_office = set(self._make_in_office_request().split('\n'))
        if len(self.in_office_old) == 0:
            self.in_office_old = self.in_office
            return
        come = self.in_office - self.in_office_old
        gone = self.in_office_old - self.in_office
        for user in my_data.data.keys():
            for alert_user in my_data.data[str(user)].get('alert_users', []):
                if alert_user in come:
                    my_bot.send_message(user, '👨🏻‍💻️ {} сейчас в офисе!'.format(alert_user))
                if alert_user in gone:
                    my_bot.send_message(user, '🙇🏻 {} теперь не в офисе!'.format(alert_user))
        self.in_office_old = self.in_office

    def _make_in_office_request(self):
        response = requests.get(self.in_url, auth=(tokens.auth_login, tokens.auth_pswd))
        return response.text

    def user_state(self, message):
        today = datetime.today()

        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(today)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(today)))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        my_bot.reply_to(message, self.state_format(response.text), parse_mode="HTML")


my_data = DataManager()
my_acs = AcsManager()
