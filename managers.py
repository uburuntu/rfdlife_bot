# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import json
from calendar import monthrange
from datetime import datetime, timedelta

import requests

import config
import tokens
from utils import global_lock, my_bot, is_non_zero_file


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

    def register_user(self, message):
        self.data[str(message.from_user.id)] = dict()
        sent = my_bot.send_message(message.from_user.id, 'Your number in Acs? Starting from 5059')
        my_bot.register_next_step_handler(sent, self.set_user_name)

    def set_user_name(self, message):
        # Todo: check existing
        if message.text.isdigit():
            self.data[str(message.from_user.id)]['name'] = str(message.text)
            self.register_user_finish(message)
        else:
            my_bot.send_message(message.from_user.id, 'Failure! Need number')

            # sent = my_bot.send_message(message.from_user.id, 'Work time?')
            # my_bot.register_next_step_handler(sent, self.set_user_week_work_time)

    def set_user_week_work_time(self, message):
        self.data[str(message.from_user.id)]['week_work_time'] = str(message.text)

        self.register_user_finish(message)

    def register_user_finish(self, message):
        self.save()
        my_bot.send_message(message.from_user.id, 'Success! Now use /week')
        # self.dump_file_to_admin()

    def get_user_name(self, message):
        # Todo: check existing
        return self.data.get(str(message.from_user.id), {}).get('name', '5059')


class AcsManager:
    def __init__(self):
        self.api_url = 'https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/index-text'

    @staticmethod
    def time_format(time):
        return time.strftime('%Y-%m-%d')

    def year_time(self, message):
        today = datetime.today()
        year_start = today.replace(day=1, month=1)
        year_end = today.replace(day=31, month=12)
        self._make_request(message, year_start, year_end)

    def month_time(self, message):
        today = datetime.today()
        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])
        self._make_request(message, month_start, month_end)

    def week_time(self, message):
        today = datetime.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        self._make_request(message, week_start, week_end)

    def day_time(self, message):
        today = datetime.today()
        self._make_request(message, today, today)

    def _make_request(self, message, start_date=None, end_date=None):
        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(start_date)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(end_date)),
                   ('AcsTabelIntermediadateSearch[summary_table]', '1'))

        response = requests.get(self.api_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        my_bot.reply_to(message, response.text)


my_data = DataManager()
my_acs = AcsManager()
