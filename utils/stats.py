# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
from collections import Counter
from datetime import datetime

import config
from utils.common_utils import bold, link, my_bot
from utils.data_manager import my_data
from tabulate import tabulate

def stats(message):
    users_count = len(my_data.list_users())
    alerts_count = 0

    for chat_id, user in my_data.data.items():
        alerts_count += len(user.get('alert_users', []))

    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()

    user_commands = re.findall('(?:User )(\d+)(?:.*called)', file_text)
    user_callbacks = re.findall('(?:User )(\d+)(?:.*callbacked)', file_text)
    commands = re.findall('(?:User.*called )(/\w*)(?:\s)', file_text)

    user_commands_counter = Counter(user_commands)
    user_callbacks_counter = Counter(user_callbacks)

    user_id = str(message.from_user.id)
    user_commands_count = user_commands_counter[user_id]
    user_callbacks_count = user_callbacks_counter[user_id]

    user_pos = user_commands_counter.most_common().index((user_id, user_commands_count)) + 1
    all_commands_count = sum(user_commands_counter.values())
    all_callbacks_count = sum(user_callbacks_counter.values())


    days_from_birthday = (datetime.today() - datetime(year=2018, month=2, day=9)).days

    text = f'Бот родился 9 февраля 2018 и сегодня его {bold(days_from_birthday)} день!\n' \
           f'Пользователей бота: {bold(users_count)}\n' \
           f'Команд вызвано: {bold(all_commands_count)}\n' \
           f'Суммарно отслеживаемых сотрудников: {bold(alerts_count)}\n\n'

    text += 'Вы использовали {} команд и находитесь на {} месте, вызвав {}% команд\n\n' \
            ''.format(bold(user_commands_count),
                      bold(user_pos),
                      bold(round(100 * user_commands_count / all_commands_count, 2)))

    text += 'Вами нажато кнопок: {}, всеми: {}\n\n'.format(bold(user_callbacks_count), bold(all_callbacks_count))

    top_count = 5
    commands_counter = Counter(commands)
    commands_most = commands_counter.most_common(top_count)
    text += f'Топ {top_count} команд по вызовам:\n'
    for i in range(top_count):
        text += f'  {i+1}. {commands_most[i][0]} — {bold(commands_most[i][1])}\n'

    my_bot.reply_to(message, text, parse_mode='HTML')


def users_stats(message):
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()

    users_commands = re.findall('(?:User )(\d+)(?:.*called)', file_text)
    users_callbacks = re.findall('(?:User )(\d+)(?:.*callbacked)', file_text)

    user_commands_counter = Counter(users_commands)
    users_callbacks_counter = Counter(users_callbacks)

    table, tables = [], []
    for user_id, user in my_data.data.items():
        table.append([user['who'], user_commands_counter[user_id], users_callbacks_counter[user_id]])
        if len(table) % 75 == 0:
            tables.append(table)
            table.clear()
    if len(table) != 0:
        tables.append(table)

    for table in tables:
        text = tabulate(table, headers=('Пользователь', 'Команд', 'Кнопок'), tablefmt='simple')
        my_bot.reply_to(message, '<pre>{}</pre>'.format(text), parse_mode='HTML')


def users(message):
    text = 'Список пользователей бота:\n\n'
    for count, (user_id, user) in enumerate(my_data.data.items(), start=1):
        text += '{}. {}\n'.format(count, link(user['who'], user_id))

    my_bot.reply_to(message, text, parse_mode='HTML')


def commands(message):
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()
        commands = re.findall('(?:User.*called )(/\w*)(?:\s)', file_text)

    commands_counter = Counter(commands)
    commands_most = commands_counter.most_common()

    text = 'Список команд бота:\n\n'
    count = 1
    for cmd in commands_most:
        text += '{}. {} — {}\n'.format(count, *cmd)
        count += 1
    my_bot.reply_to(message, '{}'.format(text), parse_mode='HTML')
