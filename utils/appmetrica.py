import json

import requests


class AppMetrica:
    def __init__(self, appmetrica_token, application_id):
        self.appmetrica_token = appmetrica_token
        self.application_id = application_id
        self.POST_API_URL = 'https://api.appmetrica.yandex.com/logs/v1/import/events'

    @staticmethod
    def dict_from_update(update):
        # Можно модифицировать для сбора конкретной информации
        data = dict()

        data['date'] = update.date
        data['message_id'] = update.message_id
        data['content_type'] = update.content_type

        user = update.from_user
        data['from'] = dict()
        data['from']['id'] = user.id
        data['from']['first_name'] = user.first_name
        if isinstance(user.last_name, str):
            data['from']['last_name'] = user.last_name
        if isinstance(user.username, str):
            data['from']['username'] = user.username
        if isinstance(user.language_code, str):
            data['from']['language_code'] = user.language_code

        chat = update.chat
        data['chat'] = dict()
        data['chat']['id'] = chat.id
        data['chat']['type'] = chat.type
        if isinstance(chat.title, str):
            data['chat']['title'] = chat.title
        if isinstance(chat.username, str):
            data['chat']['username'] = chat.username

        text = update.text
        if isinstance(text, str):
            data['text'] = text
            if update.entities is not None:
                for entity in update.entities:
                    if entity.type == 'bot_command':
                        data['bot_command'] = text[entity.offset:entity.length].split('@')[0]
                        break

        return data

    def track(self, update):
        # API Manual: tech.yandex.ru/appmetrica/doc/mobile-api/post/post-import-events-docpage/
        data = self.dict_from_update(update)
        event_name = data.get('bot_command', 'text')

        payload = (
            # Required fields
            ('post_api_key', self.appmetrica_token),
            ('application_id', self.application_id),
            ('event_name', event_name),
            ('event_timestamp', data['date']),
            # Optional fields
            ('profile_id', data['from']['id']),
            ('device_locale', data['from'].get('language_code', '')),
            ('event_json', json.dumps(data, ensure_ascii=False)),
        )

        r = requests.post(self.POST_API_URL, params=payload)
        return r.ok
