import time
from functools import wraps

import requests
from flask import Blueprint, render_template, current_app, request, redirect, \
    session

from app.models import fetch_friends, ModelError, fetch_access_data, \
    fetch_user_data

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
def login():
    if logged_in():
        return redirect('/')
    return render_template('login.html', url=current_app.config['AUTH_URL'])


@auth_blueprint.route('/auth_callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code')
    if not code:
        return render_template('error.html', message='There is no code')

    try:
        access_data = fetch_access_data(code)
        user_data = fetch_user_data(access_data['user_id'],
                                    access_data['access_token'])
    except ModelError as e:
        return render_template('error.html', message=e.message)

    session['username'] = f"{user_data['first_name']} {user_data['last_name']}"
    session.update(access_data)
    return redirect('/')


@auth_blueprint.route('/', methods=['GET'])
@require_auth
def friends():
    username = session['username']

    try:
        friends_dict = fetch_friends(session['user_id'],
                                     session['access_token'], 5)
    except ModelError as e:
        return render_template('error.html', message=e.message)

    return render_template('friends.html', username=username,
                           friends=friends_dict)


@auth_blueprint.route('/logout', methods=['GET'])
@require_auth
def logout():
    session.clear()
    return redirect('/login')
