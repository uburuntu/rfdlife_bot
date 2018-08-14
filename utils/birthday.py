import random
from datetime import datetime

import bs4
import requests

import tokens
from utils.acs_manager import my_acs
from utils.common_utils import action_log, code, my_bot, skip_exception, subs_notify
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


@skip_exception(requests.exceptions.ConnectionError)
def birthday_check():
    action_log('Scheduled job: launched birthday check')

    drs = birthdays_get()

    today = datetime.today().strftime('%d.%m')
    names = ''

    for date, name in drs:
        if date == today:
            names += '{} {}\n'.format(random.choice(happy_emoji), code(name))

    if len(names) > 0:
        text = 'Сегодня день рождения {}:\n\n{}'.format(names, 'отмечает' if len(names) == 1 else 'отмечают')
        subs_notify(my_data.list_users(for_what='morning_birthdays'), text)


def birthdays_show(message):
    drs = birthdays_get()
    if len(drs) == 0:
        my_bot.reply_to(message, my_acs.asc_unaccessible_error, parse_mode='HTML')
        return

    text = 'Ближайшие дни рождения {}:\n\n'.format(random.choice(happy_emoji))

    for date, name in drs:
        text += '{} — {}\n'.format(date, code(name))

    my_bot.reply_to(message, text, parse_mode='HTML')
