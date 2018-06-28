# !/usr/bin/env python
# _*_ coding: utf-8 _*_
from telebot.types import LabeledPrice

import tokens
from utils.common_utils import my_bot


def donate(message):
    if tokens.provider_token == '':
        my_bot.reply_to(message, 'Не подключен токен оплаты!')
        return

    my_bot.send_invoice(message.chat.id, title='Поддержка разработки бота',
                        description='Хочется есть, помогите 😞',
                        provider_token=tokens.provider_token,
                        currency='RUB',
                        prices=[LabeledPrice(label='На сникерс', amount=5000)],
                        start_parameter='donate-50',
                        invoice_payload='donate-50')

    my_bot.send_invoice(message.chat.id, title='Поддержка разработки бота | Plus',
                        description='Очень хочется есть, помогите 😩',
                        provider_token=tokens.provider_token,
                        currency='RUB',
                        prices=[LabeledPrice(label='На обед', amount=25000)],
                        start_parameter='donate-250',
                        invoice_payload='donate-250')


def pre_checkout(pre_checkout_query):
    my_bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                     error_message='Возникла очень грустная ошибка, попробуйте заново')


def got_payment(message):
    my_bot.reply_to(message,
                    'Ура! Оплата на `{} {}` прошла успешно!\n\n'
                    'Вы получаете статус Premium пользователя бота 😎'
                    ''.format(message.successful_payment.total_amount / 100, message.successful_payment.currency),
                    parse_mode='Markdown')
