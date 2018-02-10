# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import json

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
        self.url = 'https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/index-text?' \
                   'AcsTabelIntermediadateSearch%5Bstaff_id%5D={}&' \
                   'AcsTabelIntermediadateSearch%5Bdate_pass_first%5D=2018-02-05&' \
                   'AcsTabelIntermediadateSearch%5Bdate_pass_last%5D=2018-02-09&' \
                   'AcsTabelIntermediadateSearch%5Bsummary%5D=0&' \
                   'AcsTabelIntermediadateSearch%5Bsummary_table%5D=0&' \
                   'AcsTabelIntermediadateSearch%5Bsummary_table%5D=1&' \
                   'AcsTabelIntermediadateSearch%5Bsummary_table_by_day%5D=0'

    def res(self, message):
        response = requests.get(self.url.format(my_data.get_user_name(message)),
                                auth=(tokens.auth_login, tokens.auth_pswd))
        # print(response)
        my_bot.reply_to(message, response.text)


my_data = DataManager()
my_acs = AcsManager()
