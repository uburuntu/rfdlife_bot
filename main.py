#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import time

import requests

import config
import tokens
from utils import admin_tools, birthday, chai, donate, playroom, stats
from utils.acs_manager import my_acs
from utils.common_utils import action_log, bold, bot_admin_command, botan, chai_user_command, check_outdated_callback, \
    command_with_delay, commands_handler, cut_long_text, dump_messages, global_lock, is_command, link_user, \
    message_dump_lock, my_bot, my_bot_name, scheduler, subs_notify, user_action_log
from utils.data_manager import my_data


@my_bot.message_handler(func=commands_handler(['/start']))
def command_start(message):
    user_action_log(message, "called " + message.text)
    split = message.text.split()
    if len(split) == 1:
        if not my_data.is_registered(message):
            user_action_log(message, "not registered to call: " + message.text)
            my_data.register_user(message)
            return
        with open(config.FileLocation.cmd_start, 'r', encoding='utf-8') as file:
            my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    else:
        deep_link = split[1]
        if deep_link.startswith('donate'):
            donate.donate(message)


@my_bot.message_handler(func=commands_handler(['/help']))
@my_data.command_need_name
def command_start(message):
    user_action_log(message, "called " + message.text)
    with open(config.FileLocation.cmd_help, 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)
    if message.from_user.id in config.admin_ids:
        with open(config.FileLocation.cmd_help_admin, 'r', encoding='utf-8') as file:
            my_bot.reply_to(message, file.read(), parse_mode="HTML", disable_web_page_preview=True)


@my_bot.message_handler(func=commands_handler(['/restart', '/reset']))
@my_data.command_need_name
def command_restart(message):
    user_action_log(message, "called " + message.text)
    my_data.register_user(message)


@my_bot.message_handler(func=commands_handler(['/year']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_year(message):
    user_action_log(message, "called " + message.text)
    my_acs.year_time(message)


@my_bot.message_handler(func=commands_handler(['/month']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_month(message):
    user_action_log(message, "called " + message.text)
    my_acs.month_time(message)


@my_bot.message_handler(func=commands_handler(['/week']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_week(message):
    user_action_log(message, "called " + message.text)
    my_acs.week_time(message)


@my_bot.message_handler(func=commands_handler(['/day']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_day(message):
    user_action_log(message, "called " + message.text)
    my_acs.day_time(message)


@my_bot.message_handler(func=commands_handler(['/state']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_day(message):
    user_action_log(message, "called " + message.text)
    my_acs.user_state(message)


@my_bot.message_handler(func=commands_handler(['/in_office']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_in_office(message):
    user_action_log(message, "called " + message.text)
    my_acs.in_office_now(message)


@my_bot.message_handler(func=commands_handler(['/chai']))
@chai_user_command
@command_with_delay(delay=15 * 60)
def command_chai(message):
    user_action_log(message, "called " + message.text)
    chai.chai(message)


@my_bot.message_handler(func=commands_handler(['/ch']))
@chai_user_command
@command_with_delay(delay=1)
def command_ch(message):
    user_action_log(message, "called " + message.text)
    chai.chai_message(message)


@my_bot.message_handler(func=commands_handler(['/alert_add']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert_add(message):
    user_action_log(message, "called " + message.text)
    my_data.add_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/alert_erase']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert_erase(message):
    user_action_log(message, "called " + message.text)
    my_data.erase_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/alert']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert(message):
    user_action_log(message, "called " + message.text)
    my_data.list_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/birthdays']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert(message):
    user_action_log(message, "called " + message.text)
    birthday.birthdays_show(message)


@my_bot.message_handler(func=commands_handler(['/stats']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert(message):
    user_action_log(message, "called " + message.text)
    stats.stats(message)


@my_bot.message_handler(func=commands_handler(['/playroom']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_playroom(message):
    user_action_log(message, "called " + message.text)
    playroom.playroom_show(message)


@my_bot.message_handler(func=commands_handler(['/kitchen']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_playroom(message):
    user_action_log(message, "called " + message.text)
    playroom.kitchen_show(message)


@my_bot.message_handler(func=commands_handler(['/donate']))
@command_with_delay(delay=1)
def command_alert(message):
    user_action_log(message, "called " + message.text)
    donate.donate(message)


@my_bot.message_handler(func=commands_handler(['/settings']))
@command_with_delay(delay=1)
def command_settings(message):
    user_action_log(message, "called " + message.text)
    my_data.get_user_settings(message.from_user.id).show_settings_message(message)


@my_bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout(pre_checkout_query):
    donate.pre_checkout(pre_checkout_query)


@my_bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_action_log(message, "payed money!")
    donate.got_payment(message)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('chai'))
@check_outdated_callback(delay=15 * 60, cmd='/chai')
def callback_chai(call):
    user_action_log(call, "callbacked " + call.data)
    chai.chai_callback(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('in_office'))
def callback_in_office(call):
    user_action_log(call, "callbacked " + call.data)
    my_acs.in_office_update(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('settings'))
@check_outdated_callback(delay=15 * 60, cmd='/settings')
def callback_settings(call):
    user_action_log(call, "callbacked " + call.data)
    my_data.get_user_settings(call.from_user.id).settings_update(call)
    my_data.save()


@my_bot.message_handler(func=commands_handler(['/feedback']))
@command_with_delay(delay=1)
def command_day(message):
    user_action_log(message, "called " + message.text)
    split = message.text.split(' ', 1)
    if len(split) > 1:
        subs_notify(config.admin_ids, 'Обратная связь от {}: {}'.format(link_user(message.from_user), split[1]))
    else:
        my_bot.reply_to(message, 'Использование: /feedback <ваше обращение>')


@my_bot.message_handler(func=commands_handler(['/notify_all']))
@bot_admin_command
@command_with_delay(delay=1)
def command_day(message):
    user_action_log(message, "called " + message.text)
    split = message.text.split(' ', 1)
    if len(split) > 1:
        subs_notify(my_data.list_users(), '{}\n\n{}'.format(bold('Оповещение пользователей бота'), split[1]))


@my_bot.message_handler(func=commands_handler(['/log']))
@bot_admin_command
def get_log(message):
    user_action_log(message, "called " + message.text)
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        lines = file.readlines()[-100:]
        for text in cut_long_text(''.join(lines)):
            my_bot.reply_to(message, "{}".format(text))


@my_bot.message_handler(func=commands_handler(['/dump']))
@bot_admin_command
def command_dump(message):
    user_action_log(message, "called " + message.text)
    my_data.dump_file(message)


@my_bot.message_handler(func=commands_handler(['/users']))
def command_users(message):
    user_action_log(message, "called " + message.text)
    stats.users(message)


@my_bot.message_handler(func=commands_handler(['/commands']))
def command_commands(message):
    user_action_log(message, "called " + message.text)
    stats.commands(message)


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
    if tokens.botan_token != '':
        for message in messages:
            botan.track(message)
    dump_messages(messages)


while __name__ == '__main__':
    try:
        if os.path.isfile(config.FileLocation.bot_killed):
            os.remove(config.FileLocation.bot_killed)

        action_log("Running bot!")

        scheduler.add_job(my_acs.in_office_alert, 'interval', id='in_office_alert', replace_existing=True, seconds=60)
        scheduler.add_job(birthday.birthday_check, 'cron', id='birthday_check', replace_existing=True, hour=11)

        # my_bot.skip_pending = True

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
