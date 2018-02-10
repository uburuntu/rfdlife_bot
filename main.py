#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import json
import os
import re
import time

import requests

import config
import tokens
from commands import admin_tools
from utils import my_bot, my_bot_name, commands_handler, is_command, bot_admin_command, \
    action_log, user_action_log, dump_messages, global_lock, message_dump_lock


def is_non_zero_file(file_path):
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0


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
            json.dump(self.data, file)
        global_lock.release()

    def dump_file_to_admin(self):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                my_bot.send_message(config.admin_id, file.read())
            global_lock.release()

    def register_user(self, message):
        self.data[str(message.from_user.id)] = dict()
        sent = my_bot.send_message(message.from_user.id, 'Your number in Acs? Starting from 5059')
        my_bot.register_next_step_handler(sent, self.set_user_name)

    def set_user_name(self, message):
        # Todo: check existing
        if message.text.isdigit ():
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
        return self.data.get(str(message.from_user.id), {}).get('name', '')


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
        response = requests.get(self.url.format(my_data.get_user_name(message)), auth=(tokens.auth_login, tokens.auth_pswd))
        # print(response)
        my_bot.reply_to(message, response.text)


my_data = DataManager()
my_acs = AcsManager()


@my_bot.message_handler(func=commands_handler(['/start']))
def default_messages(message):
    command = message.text.lower().split()[0]
    command_raw = re.split("@+", command)[0]
    with open(config.file_location[command_raw], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    my_data.register_user(message)
    user_action_log(message, "called that command: {}".format(command))


@my_bot.message_handler(func=commands_handler(['/week']))
def default_messages(message):
    my_acs.res(message)


@my_bot.message_handler(func=commands_handler(['/dump']))
def default_messages(message):
    my_data.dump_file_to_admin()


@my_bot.message_handler(func=is_command())
@bot_admin_command
def admin_tools(message):
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != my_bot_name:
        return
    command = parts[0].lower()
    if command == "/update":
        admin_tools.update_bot(message)
    elif command == "/kill":
        admin_tools.kill_bot(message)


# All messages handler
def handle_messages(messages):
    dump_messages(messages)


while __name__ == '__main__':
    try:
        if os.path.isfile(config.file_location['bot_killed']):
            os.remove(config.file_location['bot_killed'])

        action_log("Running bot!")

        # Запуск Long Poll бота
        my_bot.set_update_listener(handle_messages)
        my_bot.polling(none_stop=True, interval=1, timeout=60)
        time.sleep(1)

    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except requests.exceptions.ReadTimeout as e:
        action_log("Read Timeout. Because of Telegram API. We are offline. Reconnecting in 5 seconds.")
        time.sleep(5)

    # если пропало соединение, то пытаемся снова
    except requests.exceptions.ConnectionError as e:
        action_log("Connection Error. We are offline. Reconnecting...")
        time.sleep(5)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RecursionError as e:
        action_log("Recursion Error. Restarting...")
        os._exit(0)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        action_log("Runtime Error. Retrying in 3 seconds.")
        time.sleep(3)

    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        action_log("Unicode Encode Error. Someone typed in cyrillic. Retrying in 3 seconds.")
        time.sleep(3)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        action_log("Keyboard Interrupt. Good bye.")
        global_lock.acquire()
        message_dump_lock.acquire()
        os._exit(0)
