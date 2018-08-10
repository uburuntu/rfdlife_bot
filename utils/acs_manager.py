import re
from calendar import monthrange
from datetime import datetime, timedelta

import numpy
import requests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame, read_html
from telebot import types

import config
import tokens
from utils.common_utils import TimeMemoize, bold, is_non_zero_file, my_bot, skip_exception
from utils.data_manager import my_data


class AcsManager:
    def __init__(self):
        self.acs_url = 'https://corp.rfdyn.ru/index.php/acs-tabel-intermediadate/index-text'
        self.in_url = 'https://corp.rfdyn.ru/index.php/site/now-in-office-text'
        self.vacation_url = 'https://corp.rfdyn.ru/index.php/site/team-calendar'

        self.in_office = set()
        self.in_office_old = set()

        self.asc_unaccessible_error = 'Сервер СКД сейчас недоступен :('

        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(types.InlineKeyboardButton(text='🔄', callback_data='in_office_update'))

    @staticmethod
    def time_format(time):
        return time.strftime('%Y-%m-%d')

    @staticmethod
    def remain_time(start_date, end_date, week_work_hours, time_in):
        # Some strange code for calc remain time
        work_days = numpy.busday_count(start_date, end_date) if start_date != end_date else int(
                start_date.weekday() < 5)
        work_time_need = week_work_hours / 5 * work_days
        time_split = [int(x) for x in time_in.split(':')]
        remain_secs = (timedelta(hours=work_time_need) - timedelta(hours=time_split[0], minutes=time_split[1],
                                                                   seconds=time_split[2])).total_seconds()
        below_zero = '-' if remain_secs < 0 else ''
        remain_hours, remain_secs = divmod(abs(remain_secs), 60 * 60)
        remain_minutes, remain_secs = divmod(remain_secs, 60)
        return '{}{:.0f}:{:02.0f}:{:02.0f}'.format(below_zero, remain_hours, remain_minutes, remain_secs)

    @staticmethod
    def reply_format(text, start_date, end_date, week_work_hours):
        if is_non_zero_file(config.FileLocation.acs_answer):
            with open(config.FileLocation.acs_answer, 'r', encoding='utf-8') as file:
                split = text.split()
                nice = file.read()
                return nice.format(last_name=split[-5], first_name=split[-4],
                                   interval_beg=AcsManager.time_format(start_date),
                                   interval_end=AcsManager.time_format(end_date),
                                   time_in=split[-2], time_all=split[-1],
                                   remain=AcsManager.remain_time(start_date, end_date, week_work_hours, split[-2]))
        return text

    @staticmethod
    def state_format(text):
        if is_non_zero_file(config.FileLocation.acs_state_answer):
            with open(config.FileLocation.acs_state_answer, 'r', encoding='utf-8') as file:
                split = text.split()
                nice = file.read()
                if len(split) > 17:
                    return nice.format(split[-6], split[-5], 'В офисе' if split[18] == 'Вход' else 'Не в офисе',
                                       split[-2])
                return '🌴 Не в офисе сегодня 🌴'
        return text

    @staticmethod
    def year_time(day):
        return day.replace(day=1, month=1), day.replace(day=31, month=12)

    @staticmethod
    def month_time(day):
        return day.replace(day=1), day.replace(day=monthrange(day.year, day.month)[1])

    @staticmethod
    def week_time(day):
        week_start = day - timedelta(days=day.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    def reply_time_data(self, user_id, cmd, day):
        if cmd == 'year':
            beg, end = self.year_time(day)
        elif cmd == 'month':
            beg, end = self.month_time(day)
        elif cmd == 'week':
            beg, end = self.week_time(day)
        else:
            beg, end = day, day

        if abs(datetime.today().year - day.year) > 4:
            return 'Иногда нужно остановиться и насладиться текущим моментом 🦄', None

        prev, next = beg - timedelta(days=1), end + timedelta(days=1)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
                types.InlineKeyboardButton(text='⬅️',
                                           callback_data='time_{}_{}'.format(cmd, prev.strftime('%d/%m/%Y'))),
                types.InlineKeyboardButton(text='🔄', callback_data='time_{}_{}'.format(cmd, day.strftime('%d/%m/%Y'))),
                types.InlineKeyboardButton(text='➡️',
                                           callback_data='time_{}_{}'.format(cmd, next.strftime('%d/%m/%Y'))))
        return self._make_time_request(user_id, beg, end), keyboard

    def reply_time_update(self, call):
        split = call.data.split('_')
        cmd = split[1]
        day = datetime.strptime(split[2], '%d/%m/%Y')
        text, keyboard = self.reply_time_data(call.from_user.id, cmd, day)
        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='✅  Сообщение обновлено')
        my_bot.edit_message_text(text,
                                 chat_id=call.message.chat.id, message_id=call.message.message_id,
                                 reply_markup=keyboard, parse_mode='HTML')

    def reply_time(self, message):
        split = re.findall('/(\w*)(?:@\w*)?\s*([\d/]*)', message.text)[0]
        cmd = split[0]
        try:
            day = datetime.today() if split[1] == '' else datetime.strptime(split[1], '%d/%m/%y')
        except ValueError:
            day = datetime.today()
        text, keyboard = self.reply_time_data(message.from_user.id, cmd, day)
        my_bot.reply_to(message, text, reply_markup=keyboard, parse_mode='HTML')

    def _make_time_request(self, user_id, start_date, end_date):
        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(user_id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(start_date)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(end_date)),
                   ('AcsTabelIntermediadateSearch[summary_table]', '1'))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        return self.reply_format(response.text, start_date, end_date,
                                 my_data.get_user_settings(user_id)[
                                     'week_work_hours']) if response.ok else self.asc_unaccessible_error

    def in_office_now_text(self, user_id=0):
        in_office_txt = self._make_in_office_request()
        for alert_user in my_data.data.get(str(user_id), {}).get('alert_users', []):
            in_office_txt = in_office_txt.replace(alert_user, bold(alert_user))
        return '👥 ' + in_office_txt

    def in_office_now(self, message):
        text = self.in_office_now_text(message.from_user.id)
        my_bot.reply_to(message, text, reply_markup=self.keyboard, parse_mode='HTML')

    def in_office_update(self, call):
        message = call.message
        text = self.in_office_now_text(message.chat.id)
        my_bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=text, parse_mode='HTML')
        my_bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                         reply_markup=self.keyboard)
        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='✅  Данные обновлены')

    @skip_exception(requests.exceptions.ConnectionError)
    def in_office_alert(self):
        def need_alert():
            if my_data.get_user_settings(user_id)['alert_about_users'] == 'on':
                return True
            if my_data.get_user_settings(user_id)['alert_about_users'] == 'when_in_office':
                return self.is_user_in_office(user_id)

        self.in_office = set(self._make_in_office_request().split('\n'))
        if len(self.in_office) == 1:
            return
        if len(self.in_office_old) == 0:
            self.in_office_old = self.in_office
            return
        come = self.in_office - self.in_office_old
        gone = self.in_office_old - self.in_office

        for user_id, user in my_data.data.items():
            if need_alert():
                for alert_user in user.get('alert_users', []):
                    if alert_user in come:
                        my_bot.send_message(user_id, '👨🏻‍💻️ {} сейчас в офисе!'.format(alert_user))
                    if alert_user in gone:
                        my_bot.send_message(user_id, '🙇🏻 {} теперь не в офисе!'.format(alert_user))
        self.in_office_old = self.in_office

    def _make_in_office_request(self):
        response = requests.get(self.in_url, auth=(tokens.auth_login, tokens.auth_pswd))
        return response.text if response.ok else ''

    def user_state(self, message):
        today = datetime.today()

        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(message.from_user.id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(today)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(today)))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        answer = self.state_format(response.text) if response.ok else self.asc_unaccessible_error
        my_bot.reply_to(message, answer, parse_mode='HTML')

    @TimeMemoize(delay=5 * 60 + 5)
    def is_user_in_office(self, user_id):
        today = datetime.today()

        payload = (('AcsTabelIntermediadateSearch[staff_id]', my_data.get_user_name(user_id)),
                   ('AcsTabelIntermediadateSearch[date_pass_first]', self.time_format(today)),
                   ('AcsTabelIntermediadateSearch[date_pass_last]', self.time_format(today)))

        response = requests.get(self.acs_url, auth=(tokens.auth_login, tokens.auth_pswd), params=payload)
        if response.ok:
            split = response.text.split()
            if len(split) > 17:
                return split[18] == 'Вход'
        return False

    def _make_vacation_request(self, date):
        payload = (('LeaveSearch[month]', date.month),
                   ('LeaveSearch[year]', date.year),
                   ('LeaveSearch[group]', ""))
        try:
            auth = (tokens.auth_login, tokens.auth_pswd)
            response = requests.get(self.vacation_url, auth=auth, params=payload)
            list_of_data_frames = read_html(response.text)
            return list_of_data_frames[0]
        except:
            return DataFrame()

    def _vacation_state(self, state):
        return (state == 'О') or (state == 'Вс') or (state == 'Уо')

    def _find_vacation_end(self, calendar_table, user_id, start):
        if not self._vacation_state(calendar_table[start][user_id]):
            return start
        for i in range(start, calendar_table.shape[1]):
            if not self._vacation_state(calendar_table[i][user_id]):
                return i
        return calendar_table.shape[1]

    @TimeMemoize(delay=15 * 60 + 42)
    def _on_vacation_now_text(self, date):
        curr_month_date = date
        next_month_date = curr_month_date + relativedelta(months=1)

        curr_month_table = self._make_vacation_request(curr_month_date)
        next_month_table = self._make_vacation_request(next_month_date)

        text = ""
        if curr_month_table.empty or next_month_table.empty:
            return text;

        vacation_list = list()
        for user_id in range(2, curr_month_table.shape[0]):
            curr_state = curr_month_table[curr_month_date.day][user_id]
            if self._vacation_state(curr_state):
                # calculate the end of vacation (first working day)
                vacation_end = self._find_vacation_end(curr_month_table, user_id, curr_month_date.day)
                if vacation_end == curr_month_table.shape[1]:
                    vacation_end = self._find_vacation_end(next_month_table, user_id, 1)
                    vacation_end_date = datetime(next_month_date.year, next_month_date.month, vacation_end)
                else:
                    vacation_end_date = datetime(curr_month_date.year, curr_month_date.month, vacation_end)
                vacation_list.append((curr_month_table[0][user_id], vacation_end_date))

        if vacation_list:
            text = "🌴 Сейчас в отпуске:\n"
            for item in vacation_list:
                text += "{} (до {}) \n".format(item[0], self.time_format(item[1]))
        else:
            text = "💻️ Сейчас все сотрудники работают!\n"

        return text

    def on_vacation_now(self, message):
        text = self._on_vacation_now_text(datetime.today())
        my_bot.reply_to(message, text, parse_mode='HTML')


my_acs = AcsManager()
