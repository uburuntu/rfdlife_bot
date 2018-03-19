# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import re
from collections import Counter

import config
from managers import my_data
from utils import bold, my_bot


def stats(message):
    users_count = len(my_data.data.keys())
    alerts_count = 0

    for chat_id, user in my_data.data.items():
        alerts_count += len(user.get('alert_users', []))

    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        file_text = file.read()
        users = re.findall('(?:User )(\d+)(?:.*called)', file_text)
        commands = re.findall('(?:User.*called )(\/\w*)(?:\s)', file_text)

    user_counter = Counter(users)
    user_id = str(message.from_user.id)
    user_commands_count = user_counter[user_id]
    user_pos = user_counter.most_common().index((user_id, user_commands_count)) + 1
    all_commands_count = sum(user_counter.values())

    commands_counter = Counter(commands)
    commands_most = commands_counter.most_common(3)

    text = 'Пользователей бота: {}\n' \
           'Команд вызвано: {}\n' \
           'Суммарно отслеживаемых сотрудников: {}\n\n'.format(bold(users_count),
                                                               bold(all_commands_count),
                                                               bold(alerts_count))

    text += 'Вы использовали {} команд и находитесь на {} месте, вызвав {}% команд\n\n' \
            ''.format(bold(user_commands_count),
                      bold(user_pos),
                      bold(round(100 * user_commands_count / all_commands_count, 2)))

    text += 'Топ 3 команды по вызовам:\n' \
            '  1. {} — {}\n' \
            '  2. {} — {}\n' \
            '  3. {} — {}\n'.format(commands_most[0][0], bold(commands_most[0][1]),
                                    commands_most[1][0], bold(commands_most[1][1]),
                                    commands_most[2][0], bold(commands_most[2][1]))

    my_bot.reply_to(message, text, parse_mode='HTML')
