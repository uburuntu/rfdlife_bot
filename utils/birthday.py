# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import random
from datetime import datetime

import bs4
import requests

import tokens
from utils.acs_manager import my_acs
from utils.common_utils import action_log, my_bot, subs_notify
from utils.data_manager import my_data

happy_emoji = ['🔥', '✨', '🎂', '🍰', '🎉', '🎊', '🎁', '🎈']


def birthdays_get():
    url = 'https://corp.rfdyn.ru/'
    response = requests.get(url, auth=(tokens.auth_login, tokens.auth_pswd))
    if not response.ok:
        return []

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Если страница поменяется, то надо перенастроить парсинг
    col = soup.select('.col-lg-4')[0]
    drs = col.select('.dates-widget')

    drs_parsed = []
    for dr in drs:
        date = dr.select('p')[0].getText()
        name = dr.select('a')[1].getText()
        drs_parsed.append((date, name))

    return drs_parsed


def birthday_check():
    action_log('Scheduled job: launched birthday check')

    drs = birthdays_get()

    today = datetime.today().strftime('%d.%m')
    names = ''

    for date, name in drs:
        if date == today:
            names += '{} <code>{}</code>\n'.format(random.choice(happy_emoji), name)

    if len(names) > 0:
        text = 'Сегодня день рождения у:\n\n{}'.format(names)
        subs_notify(my_data.list_users(for_what='morning_birthdays'), text)


def birthdays_show(message):
    drs = birthdays_get()
    if len(drs) == 0:
        my_bot.reply_to(message, my_acs.asc_unaccessible_error, parse_mode='HTML')
        return

    text = 'Ближайшие дни рождения {}:\n\n'.format(random.choice(happy_emoji))

    for date, name in drs:
        text += '{} — <code>{}</code>\n'.format(date, name)

    my_bot.reply_to(message, text, parse_mode='HTML')
