import os


class Base:
    BASE_URL = 'http://localhost:5000'

    DEBUG = False
    APP_ID = '6913818'
    PERMISSIONS = '2'
    REDIRECT_URI = f'{BASE_URL}/login'
    API_VERSION = '5.92'
    VK_APP_SECRET = os.environ.get('APP_SECRET')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fake_key')

    AUTH_URL = f'https://oauth.vk.com/authorize?' \
        f"client_id={APP_ID}&" \
        f'scope={PERMISSIONS}&' \
        f'redirect_uri={REDIRECT_URI}&' \
        f'response_type=code&' \
        f'v={API_VERSION}'


class Testing(Base):
    ...


class Development(Base):
    ...


class Production(Base):
    BASE_URL = 'https://herokuap.....'
