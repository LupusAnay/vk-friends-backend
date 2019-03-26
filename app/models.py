import time

import requests
from flask import current_app


class ModelError(BaseException):
    def __init__(self, message: str):
        self.message = message


def fetch_friends(user_id: int, access_token: str, count: int) -> dict:
    payload = {
        'user_id': user_id,
        'access_token': access_token,
        'count': count,
        'fields': 'nickname,photo_200_orig,status,city',
        'v': current_app.config['API_VERSION']
    }

    response = requests.get('https://api.vk.com/method/friends.get',
                            params=payload)

    if response.status_code != 200:
        raise ModelError("Error while fetching friends")

    try:
        result = response.json()['response']['items']
    except KeyError as e:
        raise ModelError("KeyError: Wrong VK response")

    return result


def fetch_access_data(code: int) -> dict:
    payload = {'client_id': current_app.config['APP_ID'],
               'client_secret': current_app.config['VK_APP_SECRET'],
               'redirect_uri': current_app.config['REDIRECT_URI'],
               'code': code}

    response = requests.get('https://oauth.vk.com/access_token',
                            params=payload)
    if response.status_code != 200:
        raise ModelError(message='Token request error')

    data = response.json()
    data['expires_in'] = time.time() + data['expires_in']

    return data


def fetch_user_data(user_id: int, access_token: str) -> dict:
    payload = {
        'user_ids': user_id,
        'access_token': access_token,
        'fields': 'nickname',
        'v': current_app.config['API_VERSION']
    }

    response = requests.get('https://api.vk.com/method/users.get',
                            params=payload)

    if response.status_code != 200:
        raise ModelError('Error while fetching user data')
    return response.json()['response'][0]

