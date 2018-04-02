# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import json

import config
import tokens
from utils.common_utils import bold, cut_long_text, global_lock, is_non_zero_file, link_user, my_bot, subs_notify, \
    user_action_log, user_name
from utils.settings import UserSettings


class DataManager:
    def __init__(self, file_name=config.FileLocation.user_data):
        self.file_name = file_name
        self.data = dict()
        self.load()

    def load(self):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                self.data = json.load(file, cls=DataJsonDecoder)
            global_lock.release()

    def save(self):
        global_lock.acquire()
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, cls=DataJsonEncoder, indent=True, ensure_ascii=False)
        global_lock.release()

    def dump_file(self, message):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                for text in cut_long_text(file.read()):
                    my_bot.reply_to(message, text)
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

    def check_password(self, message):
        if tokens.access_pswd != "" and message.text == tokens.access_pswd:
            if self.data.get(str(message.from_user.id)) is None:
                self.data[str(message.from_user.id)] = {"authenticated": "True"}
            else:
                self.data[str(message.from_user.id)]["authenticated"] = "True"
            user_action_log(message, "successfully registered")
            my_bot.reply_to(message, "✅ Пароль верный!")
            subs_notify(config.admin_ids, '✨ Новый пользователь: {}'.format(link_user(message.from_user)))
            my_data.data[str(message.from_user.id)]['who'] = user_name(message.from_user)
            self.register_user(message)
        else:
            user_action_log(message, "entered wrong password")
            my_bot.reply_to(message, "⛔ Пароль не подошел!\n\nВызывай /start для новой попытки.")

    def register_user(self, message):
        if not self.is_registered(message):
            sent = my_bot.send_message(message.from_user.id,
                                       bold('❗️ Авторизация') + '\n\nВведи пароль:', parse_mode="HTML")
            my_bot.register_next_step_handler(sent, self.check_password)
            return

        sent = my_bot.send_message(message.from_user.id,
                                   '❓ Твой номер в '
                                   '<a href=\"https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/\">СКД</a>?\n'
                                   'Например: 5059, 5060 и т.д.', parse_mode="HTML")
        my_bot.register_next_step_handler(sent, self.set_user_name)

    def set_user_name(self, message):
        # Todo: check existing
        if message.text.isdigit():
            self.data[str(message.from_user.id)]['name'] = str(message.text)
            self.register_user_finish(message)
        else:
            my_bot.send_message(message.from_user.id, '⚠️ Ошибка, нужно указать номер')

    def register_user_finish(self, message):
        my_data.data[str(message.from_user.id)]['settings'] = UserSettings()
        self.save()
        my_bot.reply_to(message, '✅ Данные сохранены', parse_mode="HTML", disable_web_page_preview=True)
        with open(config.FileLocation.cmd_help, 'r', encoding='utf-8') as file:
            my_bot.send_message(message.from_user.id, file.read(), parse_mode="HTML", disable_web_page_preview=True)

    def list_users(self, for_what=None):
        all_users = self.data.keys()
        if for_what is None:
            return all_users
        if for_what == 'morning_birthdays':
            return [user_id for user_id in all_users if self.get_user_settings(user_id)[for_what] == 'on']

    def get_user_name(self, user_id):
        return self.data.get(str(user_id), {}).get('name', '5059')

    def get_user_settings(self, user_id):
        user = self.data[str(user_id)]
        if user.get('settings') is None:
            user['settings'] = UserSettings()
        return user['settings']

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
            my_bot.reply_to(message, '⚙️ Ваш список оповещений:\n— <code>{}</code>\n\n'
                                     'Используйте /alert_add и /alert_erase для управления списком.'
                                     ''.format('</code>\n— <code>'.join(users)), parse_mode='HTML')
        else:
            my_bot.reply_to(message, '⚙️ Ваш список оповещений пуст.\n\n'
                                     'Используйте /alert_add и /alert_erase для управления списком.')


class DataJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UserSettings):
            obj.data['__type__'] = obj.__class__.__name__
            return obj.data
        return json.JSONEncoder.default(self, obj)


class DataJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, *args, **kargs)

    @staticmethod
    def dict_to_object(d):
        if '__type__' not in d:
            return d

        obj_type = d.pop('__type__')
        try:
            if obj_type == UserSettings.__name__:
                obj = UserSettings(d)
                return obj
        except:
            d['__type__'] = obj_type
        return d


my_data = DataManager()
