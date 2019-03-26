import time
from functools import wraps

import requests
from flask import Blueprint, render_template, current_app, request, redirect, \
    session

auth_blueprint = Blueprint('auth', __name__)


def logged_in() -> bool:
    return 'user_id' in session and 'access_token' in session and \
           'expires_in' in session


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if logged_in():
            if time.time() <= session['expires_in']:
                return func(*args, **kwargs)
            else:
                session.clear()
                return redirect('/login')
        else:
            return redirect('/login')

    return wrapper


@auth_blueprint.route('/login', methods=['GET'])
def index():
    if logged_in():
        return redirect('/')
    return render_template('index.html', url=current_app.config['AUTH_URL'])


@auth_blueprint.route('/auth_callback', methods=['GET'])
def login():
    code = request.args.get('code')
    if not code:
        return render_template('auth_error.html', message='There is no code')

    payload = {'client_id': current_app.config['APP_ID'],
               'client_secret': current_app.config['VK_APP_SECRET'],
               'redirect_uri': current_app.config['REDIRECT_URI'],
               'code': code}

    response = requests.get('https://oauth.vk.com/access_token',
                            params=payload)
    if response.status_code != 200:
        return render_template('auth_error.html',
                               message='Token request error')

    data = response.json()
    data['expires_in'] = time.time() + data['expires_in']
    session.update(data)
    return redirect('/')


@auth_blueprint.route('/', methods=['GET'])
@require_auth
def friends():
    payload = {
        'user_id': session['user_id'],
        'access_token': session['access_token'],
        'count': 5,
        'fields': 'nickname,photo_200_orig,status,city',
        'v': current_app.config['API_VERSION']
    }

    response = requests.get('https://api.vk.com/method/friends.get',
                            params=payload)

    if response.status_code != 200:
        return render_template('auth_error.html', message='Not logged in')

    friends_array = response.json()['response']['items']

    return render_template('friends.html', friends=friends_array)
