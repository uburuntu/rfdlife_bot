# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import random
from datetime import datetime

import bs4
import requests

import tokens
from managers import my_data
from utils import subs_notify, action_log

happy_emoji = ['🔥', '✨', '🎂', '🍰', '🎉', '🎊', '🎁', '🎈']


def birthday_check():
    action_log('Launched birthday check')

    url = 'https://corp.rfdyn.ru/'
    response = requests.get(url, auth=(tokens.auth_login, tokens.auth_pswd))
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Если страница поменяется, то надо перенастроить парсинг
    today = datetime.today().strftime('%d.%m')
    col = soup.select('.col-lg-4')[0]
    drs = col.select('.dates-widget')

    names = ''
    for dr in drs:
        dr_date = dr.select('p')[0].getText()
        if dr_date == today:
            name = dr.select('a')[1].getText()
            names += '{} <code>{}</code>\n'.format(random.choice(happy_emoji), name)

    if len(names) > 0:
        text = 'Сегодня день рождения у:\n\n{}\n'.format(names)
        subs_notify(my_data.data.keys(), text)
