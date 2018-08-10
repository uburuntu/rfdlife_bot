from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame, read_html

import tokens
from utils.common_utils import TimeMemoize, my_bot, bold, code


def _make_vacation_request(date):
    vacation_url = 'https://corp.rfdyn.ru/index.php/site/team-calendar'

    payload = (('LeaveSearch[month]', date.month),
               ('LeaveSearch[year]', date.year),
               ('LeaveSearch[group]', ''))

    response = requests.get(vacation_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
    if response.ok:
        list_of_data_frames = read_html(response.text)
        return list_of_data_frames[0]
    return DataFrame()


def _vacation_state(state):
    return (state == 'О') or (state == 'Вс') or (state == 'Уо')


def _find_vacation_end(calendar_table, user_id, start):
    if not _vacation_state(calendar_table[start][user_id]):
        return start
    for i in range(start, calendar_table.shape[1]):
        if not _vacation_state(calendar_table[i][user_id]):
            return i
    return calendar_table.shape[1]


@TimeMemoize(delay=15 * 60 + 42)
def _on_vacation_get(date):
    curr_month_date = datetime.date(date)
    next_month_date = curr_month_date + relativedelta(months=1)

    curr_month_table = _make_vacation_request(curr_month_date)
    next_month_table = _make_vacation_request(next_month_date)

    vacations = []

    if curr_month_table.empty or next_month_table.empty:
        return vacations

    for user_id in range(2, curr_month_table.shape[0]):
        curr_state = curr_month_table[curr_month_date.day][user_id]
        if _vacation_state(curr_state):
            # Calculate the end of vacation (first working day)
            vacation_end_day = _find_vacation_end(curr_month_table, user_id, curr_month_date.day)
            if vacation_end_day == curr_month_table.shape[1]:
                vacation_end_day = _find_vacation_end(next_month_table, user_id, 1)
                vacation_end_date = datetime(next_month_date.year, next_month_date.month, vacation_end_day)
            else:
                vacation_end_date = datetime(curr_month_date.year, curr_month_date.month, vacation_end_day)
            vacations.append((curr_month_table[0][user_id], vacation_end_date))

    return vacations


def on_vacation_now(message):
    vacations = _on_vacation_get(datetime.today())
    if vacations:
        text = '🌴 {}:\n'.format(bold('Сейчас в отпуске'))
        for item in vacations:
            text += '{} — до {}\n'.format(code(item[0]), item[1].strftime('%d/%m'))
    else:
        text = '💻️ Сейчас нет сотрудников в отпуске!\n'

    my_bot.reply_to(message, text, parse_mode='HTML')
