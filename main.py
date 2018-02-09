#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import os
import re
import time

from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

import config
from commands import admin_tools
from utils import my_bot, my_bot_name, commands_handler, is_command, bot_admin_command, \
    action_log, user_action_log, dump_messages, global_lock, message_dump_lock


@my_bot.message_handler(func=commands_handler(['/start']))
def my_new_data(message):
    command = message.text.lower().split()[0]
    command_raw = re.split("@+", command)[0]
    with open(config.file_location[command_raw], 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    user_action_log(message, "called that command: {}".format(command))


@my_bot.message_handler(func=is_command())
@bot_admin_command
def admin_toys(message):
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
    except ReadTimeout as e:
        action_log("Read Timeout. Because of Telegram API. We are offline. Reconnecting in 5 seconds.")
        time.sleep(5)

    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
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
