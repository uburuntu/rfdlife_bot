# _*_ coding: utf-8 _*_

from telebot import types

from utils.common_utils import my_bot


class Setting:
    def __init__(self, show_name, statuses, statuses_emoji, help_text):
        self.show_name = show_name
        self.help_text = help_text

        if len(statuses) != len(statuses_emoji):
            raise IndexError
        self.statuses = statuses
        self.statuses_emoji = statuses_emoji
        self.len = len(statuses)
        self.curr = 0

    def get(self):
        return self.statuses[self.curr]

    def set(self, status):
        self.curr = self.statuses.index(status)

    def get_emoji(self):
        return self.statuses_emoji[self.curr]

    def defaultify(self):
        self.curr = 0

    def next(self):
        self.curr = (self.curr + 1) % self.len


class UserSettings:
    def __init__(self, data=None):
        self.settings_info = {
            'morning_birthdays':
                Setting('Дни рождения:', ['on', 'off'], ['🔔', '🔕'],
                        'Оповещение о днях рождения с утра.\n'
                        '🔔 — оповещать\n'
                        '🔕 — отключить оповещения'),
            'alert_about_users':
                Setting('Появление сотрудников:', ['on', 'when_in_office', 'off'], ['🔔', '🔔+🖥', '🔕'],
                        'Оповещение о появлении сотрудников в офисе (команда /alert).\n'
                        '🔔 — оповещать всегда\n'
                        '🔔+🖥 — оповещать только, когда я в офисе\n'
                        '🔕 — отключить оповещения')}

        if data is None:
            self.data = {}
            self.defaultify_all()
        else:
            self.data = data
            for name, setting in self.settings_info.items():
                if self.data.get(name) is not None:
                    setting.set(self.data[name])

    def __getitem__(self, item):
        return self.data[item]

    def defaultify_all(self):
        for name, setting in self.settings_info.items():
            setting.defaultify()
            self.data[name] = setting.get()

    def show_settings_message(self, message):
        my_bot.reply_to(message, 'Ваши настройки\n\nПримечание: при нажатии на кнопки слева '
                                 'появляется описание настройки', reply_markup=self.generate_settings_buttons())

    def generate_settings_buttons(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton(text="Оповещения:", callback_data="settings_dummy"))
        for name, setting in self.settings_info.items():
            keyboard.row(types.InlineKeyboardButton(text=setting.show_name, callback_data="settings_help_" + name),
                         types.InlineKeyboardButton(text=setting.get_emoji(), callback_data="settings_" + name))
        keyboard.row(types.InlineKeyboardButton(text="❎ Сброс настроек", callback_data="settings_default"))
        return keyboard

    def settings_update(self, call):
        message = call.message

        cmd_name = call.data.split('_', 1)[1]
        if cmd_name == 'dummy':
            my_bot.answer_callback_query(callback_query_id=call.id)
            return
        elif cmd_name.startswith('help'):
            setting_name = cmd_name.split('_', 1)[1]
            my_bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                         text=self.settings_info[setting_name].help_text)
            return
        elif cmd_name == 'default':
            self.defaultify_all()
        else:
            self.settings_info[cmd_name].next()
            self.data[cmd_name] = self.settings_info[cmd_name].get()

        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="✅  Настройки обновлены")
        my_bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                         reply_markup=self.generate_settings_buttons())
