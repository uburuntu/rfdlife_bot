# !/usr/bin/env python
# _*_ coding: utf-8 _*_
from config import file_location
from managers import my_data
from utils import my_bot, bold


def stats(message):
    users_count = len(my_data.data.keys())
    alerts_count = 0
    commands_count = 0

    for id, user in my_data.data.items():
        alerts_count += len(user.get('alert_users', []))

    with open(file_location['bot_logs'], 'r', encoding='utf-8') as file:
        commands_count = file.read().count('called')

    text = 'Пользователей бота: {}\n\n' \
           'Команд вызвано: {}\n\n' \
           'Суммарно отслеживаемых сотрудников: {}'.format(bold(users_count),
                                                           bold(commands_count),
                                                           bold(alerts_count))

    my_bot.reply_to(message, text, parse_mode='HTML')
