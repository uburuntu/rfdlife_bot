# !/usr/bin/env python
# _*_ coding: utf-8 _*_

from telebot import types

from utils import my_bot


def chai(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на Яндекс", url="https://ya.ru")
    keyboard.add(url_button)
    my_bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)


def chai_callback(call):
    if call.data == "chai_add":
        my_bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
