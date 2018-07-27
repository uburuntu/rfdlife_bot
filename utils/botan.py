import requests


class Botan:
    def __init__(self, botan_token):
        self.botan_token = botan_token
        self.TRACK_URL = 'https://api.botan.io/track'
        self.SHORTENER_URL = 'https://api.botan.io/s/'

    @staticmethod
    def dict_from_message(message):
        # Можно модифицировать для сбора конкретной информации
        data = dict()

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

        return data

    def track(self, message):
        try:
            data = self.dict_from_message(message)
            event_name = data.get('bot_command', 'Text message')
            r = requests.post(self.TRACK_URL,
                              params={'token': self.botan_token, 'uid': message.from_user.id, 'name': event_name},
                              data=data,
                              headers={'Content-type': 'application/json'})
            return r.json()
        except requests.exceptions.Timeout:
            # set up for a retry, or continue in a retry loop
            return False
        except (requests.exceptions.RequestException, ValueError) as e:
            # catastrophic error
            # print(e)
            return False

    def shorten_url(self, url, user_id):
        """
        Shorten URL for specified user of a bot
        """
        try:
            return requests.get(self.SHORTENER_URL,
                                params={'token': self.botan_token, 'url': url, 'user_ids': str(user_id)}
                                ).text
        except:
            return url
