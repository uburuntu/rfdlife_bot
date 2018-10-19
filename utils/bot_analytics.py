import json
import time

import requests


class BotAnalytics:
    api_url = 'https://chatbase.com/api/message'
    request_header = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def __init__(self, api_key):
        """
        Chatbase bot analytics, docs: chatbase.com/documentation/generic

        Example usage:
            analytics = BotAnalytics(api_key=chatbase_token)
            ...
            ret = analytics.track_message(message)
            if not ret.ok:
                print(ret.text)

        :param api_key: Key from chatbase.com
        """
        self.api_key = api_key
        self.session = requests.Session()

    def track(self, user_id, event_name, intent_name=None, time_stamp=None):
        """
        Track some event

        :param user_id: unique id for current user
        :param event_name: detailed event name or raw message
        :param intent_name: event's group
        :param time_stamp: UNIX-time of event
        :return: requests.Response
        """
        data = {
            'api_key'    : self.api_key,
            'platform'   : 'Telegram',
            'message'    : event_name,
            'intent'     : intent_name or event_name,
            'version'    : 'stable',
            'user_id'    : user_id,
            'not_handled': False,
            'time_stamp' : int(time_stamp or round(time.time())) * 1e3,
            'type'       : 'user',
        }

        r = self.session.post(self.api_url, data=json.dumps(data).encode(), headers=self.request_header)
        return r

    @staticmethod
    def message_event_intent(message):
        """
        This function specialized for pyTelegramBotAPI, change it for other API implementation
        """
        text = message.text
        if isinstance(text, str):
            if message.entities is not None:
                for entity in message.entities:
                    if entity.type == 'bot_command':
                        command = text[entity.offset:entity.length].split('@')[0]
                        return command, command
                else:
                    return text, 'text'
        return message.content_type, 'other'

    def track_message(self, message):
        user_id = message.from_user.id
        event_name, intent_name = self.message_event_intent(message)
        time_stamp = message.date

        return self.track(user_id, event_name, intent_name, time_stamp)

    def track_callback(self, call):
        user_id = call.from_user.id
        event_name = call.data
        intent_name = call.data.split('_')[0]

        return self.track(user_id, event_name, intent_name)
