import requests
from flask import Blueprint, render_template, current_app, request, redirect, \
    make_response, session

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/', methods=['GET'])
def index():
    if 'user_id' in session and 'access_token' in session:
        return redirect('/friends')
    return render_template('index.html', url=current_app.config['AUTH_URL'])


@auth_blueprint.route('/login', methods=['GET'])
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
    session.update(data)
    return redirect('/friends')


@auth_blueprint.route('/friends', methods=['GET'])
def friends():
    payload = {
        'user_id': session['user_id'],
        'access_token': session['access_token'],
        'count': 5,
        'fields': 'nickname',
        'v': current_app.config['API_VERSION']
    }

    response = requests.get('https://api.vk.com/method/friends.get',
                            params=payload)

    if response.status_code != 200:
        return render_template('auth_error.html', message='Not logged in')

    friends_array = response.json()['response']['items']

    return render_template('friends.html', friends=friends_array)
