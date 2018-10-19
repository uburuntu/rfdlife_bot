import os
import sys
import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler

import config
import tokens
from utils import birthday, chai, donate, playroom, stats, vacation
from utils.acs_manager import my_acs
from utils.admin_tools import kill_bot, update_bot
from utils.common_utils import action_log, bold, bot_admin_command, chai_user_command, check_outdated_callback, \
    command_with_delay, commands_handler, cut_long_text, global_lock, is_command, link, my_analytics, my_bot, \
    not_command, subs_notify, user_action_log
from utils.data_manager import my_data


@my_bot.message_handler(func=commands_handler(['/start']))
def command_start(message):
    user_action_log(message, 'called ' + message.text)
    split = message.text.split()
    if len(split) == 1:
        if not my_data.is_registered(message):
            user_action_log(message, 'not registered to call: ' + message.text)
            my_data.register_user(message)
            return
        with open(config.FileLocation.cmd_start, 'r', encoding='utf-8') as file:
            my_bot.reply_to(message, file.read(), parse_mode='HTML', disable_web_page_preview=True)
    else:
        deep_link = split[1]
        if deep_link.startswith('donate'):
            donate.donate(message)


@my_bot.message_handler(func=commands_handler(['/help']))
@my_data.command_need_name
def command_help(message):
    user_action_log(message, 'called ' + message.text)
    with open(config.FileLocation.cmd_help, 'r', encoding='utf-8') as file:
        my_bot.reply_to(message, file.read(), parse_mode='HTML', disable_web_page_preview=True)
    if message.from_user.id in config.admin_ids:
        with open(config.FileLocation.cmd_help_admin, 'r', encoding='utf-8') as file:
            my_bot.reply_to(message, file.read(), parse_mode='HTML', disable_web_page_preview=True)


@my_bot.message_handler(func=commands_handler(['/restart', '/reset']))
@my_data.command_need_name
def command_restart(message):
    user_action_log(message, 'called ' + message.text)
    my_data.register_user(message)


@my_bot.message_handler(func=commands_handler(['/year', '/month', '/week', '/day']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_date(message):
    user_action_log(message, 'called ' + message.text)
    my_acs.reply_time(message)


@my_bot.message_handler(func=commands_handler(['/state']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_state(message):
    user_action_log(message, 'called ' + message.text)
    my_acs.user_state(message)


@my_bot.message_handler(func=commands_handler(['/in_office']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_in_office(message):
    user_action_log(message, 'called ' + message.text)
    my_acs.in_office_now(message)


@my_bot.message_handler(func=commands_handler(['/vacation']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_vacation(message):
    user_action_log(message, 'called ' + message.text)
    vacation.on_vacation_now(message)


@my_bot.message_handler(func=commands_handler(['/chai']))
@chai_user_command
@command_with_delay(delay=15 * 60)
def command_chai(message):
    user_action_log(message, 'called ' + message.text)
    chai.chai(message)


@my_bot.message_handler(func=commands_handler(['/ch']))
@chai_user_command
@command_with_delay(delay=1)
def command_ch(message):
    user_action_log(message, 'called ' + message.text)
    chai.chai_message(message)


@my_bot.message_handler(func=commands_handler(['/alert_add']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert_add(message):
    user_action_log(message, 'called ' + message.text)
    my_data.add_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/alert_erase']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert_erase(message):
    user_action_log(message, 'called ' + message.text)
    my_data.erase_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/alert']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_alert(message):
    user_action_log(message, 'called ' + message.text)
    my_data.list_alert_name(message)


@my_bot.message_handler(func=commands_handler(['/birthdays']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_birthdays(message):
    user_action_log(message, 'called ' + message.text)
    birthday.birthdays_show(message)


@my_bot.message_handler(func=commands_handler(['/stats']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_stats(message):
    user_action_log(message, 'called ' + message.text)
    stats.stats(message)


@my_bot.message_handler(func=commands_handler(['/users_stats']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_users_stats(message):
    user_action_log(message, 'called ' + message.text)
    stats.users_stats(message)


@my_bot.message_handler(func=commands_handler(['/playroom']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_playroom(message):
    user_action_log(message, 'called ' + message.text)
    playroom.playroom_show(message)


@my_bot.message_handler(func=commands_handler(['/kitchen']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_kitchen(message):
    user_action_log(message, 'called ' + message.text)
    playroom.kitchen_show(message)


@my_bot.message_handler(func=commands_handler(['/camera']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_camera(message):
    user_action_log(message, 'called ' + message.text)
    playroom.camera_n_show(message)


@my_bot.message_handler(func=commands_handler(['/donate']))
@command_with_delay(delay=1)
def command_donate(message):
    user_action_log(message, 'called ' + message.text)
    donate.donate(message)


@my_bot.message_handler(func=commands_handler(['/settings']))
@my_data.command_need_name
@command_with_delay(delay=1)
def command_settings(message):
    user_action_log(message, 'called ' + message.text)
    my_data.get_user_settings(message.from_user.id).show_settings_message(message)


@my_bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout(pre_checkout_query):
    donate.pre_checkout(pre_checkout_query)


@my_bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_action_log(message, 'payed money!')
    donate.got_payment(message)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('chai'))
@check_outdated_callback(delay=15 * 60, cmd='/chai')
@my_data.callback_need_access
def callback_chai(call):
    user_action_log(call, 'callbacked ' + call.data)
    if tokens.chatbase_token != '':
        my_analytics.track_callback(call)
    chai.chai_callback(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('time'))
@my_data.callback_need_access
def callback_time(call):
    user_action_log(call, 'callbacked ' + call.data)
    if tokens.chatbase_token != '':
        my_analytics.track_callback(call)
    my_acs.reply_time_update(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('in_office'))
@my_data.callback_need_access
def callback_in_office(call):
    user_action_log(call, 'callbacked ' + call.data)
    if tokens.chatbase_token != '':
        my_analytics.track_callback(call)
    my_acs.in_office_update(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('camera'))
@my_data.callback_need_access
def callback_camera(call):
    user_action_log(call, 'callbacked ' + call.data)
    if tokens.chatbase_token != '':
        my_analytics.track_callback(call)
    playroom.update_camera(call)


@my_bot.callback_query_handler(func=lambda call: call.data.startswith('settings'))
@check_outdated_callback(delay=15 * 60, cmd='/settings')
@my_data.callback_need_access
def callback_settings(call):
    user_action_log(call, 'callbacked ' + call.data)
    if tokens.chatbase_token != '':
        my_analytics.track_callback(call)
    my_data.get_user_settings(call.from_user.id).settings_update(call)
    my_data.save()


@my_bot.message_handler(func=commands_handler(['/feedback']))
@command_with_delay(delay=1)
def command_day(message):
    user_action_log(message, 'called ' + message.text)
    split = message.text.split(' ', 1)
    if len(split) > 1:
        subs_notify(config.admin_ids, 'Обратная связь от {}: {}'
                                      ''.format(link(my_data.data[str(message.from_user.id)]['who'],
                                                     message.from_user.id), split[1]))
        my_bot.reply_to(message, 'Сообщение отправлено!')
    else:
        my_bot.reply_to(message, 'Использование: /feedback [ваше обращение]')


@my_bot.message_handler(func=commands_handler(['/reply']))
@bot_admin_command
@command_with_delay(delay=1)
def command_reply(message):
    user_action_log(message, 'called ' + message.text)
    if hasattr(message, 'reply_to_message'):
        split = message.text.split(' ', 1)
        if len(split) > 1:
            replying_msg = message.reply_to_message
            if hasattr(replying_msg, 'entities'):
                user_ids = [x.user.id for x in replying_msg.entities if x.type == 'text_mention']
                if len(user_ids) == 1:
                    my_bot.send_message(user_ids[0], '{}: {}'.format(bold('Разработчик'), split[1]),
                                        parse_mode='HTML')
                    my_bot.reply_to(message, 'Сообщение отправлено!')
                    return
    my_bot.reply_to(message, 'Использовать с ответом на фидбек: /reply [ваш ответ]')


@my_bot.message_handler(func=commands_handler(['/notify_all']))
@bot_admin_command
@command_with_delay(delay=1)
def command_notify_all(message):
    user_action_log(message, 'called ' + message.text)
    split = message.text.split(' ', 1)
    if len(split) > 1:
        subs_notify(my_data.list_users(), '{}\n\n{}'.format(bold('Оповещение пользователей бота'), split[1]),
                    me=message.from_user.id)

    else:
        my_bot.reply_to(message, 'Использование: /notify_all [ваше сообщение]')


@my_bot.message_handler(func=commands_handler(['/notify_all_test']))
@bot_admin_command
@command_with_delay(delay=1)
def command_notify_all_test(message):
    user_action_log(message, 'called ' + message.text)
    split = message.text.split(' ', 1)
    if len(split) > 1:
        subs_notify([message.from_user.id], '{}\n\n{}'.format(bold('Оповещение пользователей бота'), split[1]))


@my_bot.message_handler(func=commands_handler(['/touch_all']))
@bot_admin_command
@command_with_delay(delay=1)
def command_touch_all(message):
    user_action_log(message, 'called ' + message.text)
    for chat_id in my_data.list_users():
        my_bot.send_chat_action(chat_id, action='typing')


@my_bot.message_handler(func=commands_handler(['/log']))
@bot_admin_command
def command_log(message):
    user_action_log(message, 'called ' + message.text)
    with open(config.FileLocation.bot_logs, 'r', encoding='utf-8') as file:
        lines = file.readlines()[-100:]
        for text in cut_long_text(''.join(lines)):
            my_bot.reply_to(message, '{}'.format(text))


@my_bot.message_handler(func=commands_handler(['/dump']))
@bot_admin_command
def command_dump(message):
    user_action_log(message, 'called ' + message.text)
    my_data.dump_file(message)


@my_bot.message_handler(func=commands_handler(['/users']))
def command_users(message):
    user_action_log(message, 'called ' + message.text)
    stats.users(message)


@my_bot.message_handler(func=commands_handler(['/commands']))
def command_commands(message):
    user_action_log(message, 'called ' + message.text)
    stats.commands(message)


@my_bot.message_handler(func=is_command())
@bot_admin_command
def admin_tools(message):
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != my_bot.name:
        return
    command = parts[0].lower()
    if command == '/update':
        update_bot(message)
    elif command == '/kill':
        kill_bot(message)


@my_bot.message_handler(func=not_command())
@my_data.command_need_name
# @chai_user_command
def chai_chat(message):
    message.text = '/ch ' + message.text
    user_action_log(message, 'called ' + message.text)
    chai.chai_message(message)


# All updates handler
def handle_updates(updates):
    if tokens.chatbase_token != '':
        for update in updates:
            ret = my_analytics.track_message(update)
            if not ret.ok:
                action_log(ret.text)


if __name__ == '__main__':
    # Настройка глобальных переменных
    my_bot.set_proxy()
    my_bot.skip_pending = False
    my_bot.set_update_listener(handle_updates)
    action_log('Running bot!')

    scheduler = BackgroundScheduler()
    scheduler.add_job(my_acs.in_office_alert, 'interval', id='in_office_alert', max_instances=3, seconds=30)
    scheduler.add_job(birthday.birthday_check, 'cron', id='birthday_check', replace_existing=True, hour=11)
    scheduler.add_job(my_data.dump_file, 'cron', id='dump_file', replace_existing=True, hour=6)
    scheduler.start()

    while True:
        try:
            if os.path.isfile(config.FileLocation.bot_killed):
                os.remove(config.FileLocation.bot_killed)

            my_bot.init_name()

            # Запуск Long Poll бота
            my_bot.polling(none_stop=True)

        except requests.exceptions.ReadTimeout as e:
            action_log('Read Timeout. Reconnecting in 5 seconds.')
            time.sleep(5)

        except requests.exceptions.ConnectionError as e:
            # action_log('Connection Error. Reconnecting...')
            time.sleep(1)

        except KeyboardInterrupt as e:
            action_log('Keyboard Interrupt. Good bye.')
            global_lock.acquire()
            sys.exit(0)
