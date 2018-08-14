import json

import requests


class BotAnalytics:
    api_url = 'https://chatbase.com/api/message'

    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def dict_from_message(message):
        # Можно модифицировать для сбора конкретной информации
        data = dict()

        data['date'] = message.date
        data['message_id'] = message.message_id
        data['content_type'] = message.content_type

        user = message.from_user
        data['from'] = dict()
        data['from']['id'] = user.id
        data['from']['first_name'] = user.first_name
        if isinstance(user.last_name, str):
            data['from']['last_name'] = user.last_name
        if isinstance(user.username, str):
            data['from']['username'] = user.username
        if isinstance(user.language_code, str):
            data['from']['language_code'] = user.language_code

        chat = message.chat
        data['chat'] = dict()
        data['chat']['id'] = chat.id
        data['chat']['type'] = chat.type
        if isinstance(chat.title, str):
            data['chat']['title'] = chat.title
        if isinstance(chat.username, str):
            data['chat']['username'] = chat.username

        text = message.text
        if isinstance(text, str):
            data['text'] = text
            if message.entities is not None:
                for entity in message.entities:
                    if entity.type == 'bot_command':
                        data['bot_command'] = text[entity.offset:entity.length].split('@')[0]
                        break

        return data

    def track(self, message):
        data = self.dict_from_message(message)

        user_id = data['from']['id']
        time_stamp = data['date']
        event_name = data.get('bot_command', 'text')

        data = {
            'api_key'    : self.api_key,
            'platform'   : 'Telegram',
            'message'    : event_name,
            'intent'     : event_name,
            'version'    : '',
            'user_id'    : user_id,
            'not_handled': False,
            'feedback'   : False,
            'time_stamp' : time_stamp,
            'type'       : 'user',
        }

        r = requests.post(self.api_url, data=json.dumps(data, ensure_ascii=False),
                          headers={'Content-type': 'application/json', 'Accept': 'text/plain'})

        return r
