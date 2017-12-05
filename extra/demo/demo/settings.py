"""
Settings for sisy demo project

This is only a demo.  DO NOT use these settings for production.
This project REQUIRES Python 3.6 or higher.

You very likely will want to adjust the settings marked CHANGE ME below,
which include the IP address for the Postgres database and the Redis server.
"""

import os
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ThisIsOnlyADemoNeverPutYourActualSecretKeyInAPublicGitRepo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Remember to set this to your actual hostname(s) before running in production
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'sisy.apps.SisyConfig',
    'myapp.apps.MyappConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'demo.wsgi.application'


# We use a postgres database (not sqlite3) for the demo because
# Channels is inherently distributed, so sqlite wouldn't work.
# In fact, you might want to make sure to change the HOST
# parameter, since not all the worker machines will have the
# database running locally.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'demo',
        'USER': 'demo',
        'PASSWORD': 'demo',
        'HOST': '127.0.0.1', # CHANGE ME TO POINT TO YOUR DATABASE
        'PORT': 5432, # might want to change this too, if necessary
    }
}

# Password validation removed for demo project

AUTH_PASSWORD_VALIDATORS = [
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)], # CHANGE ME TO POINT TO YOUR REDIS SERVER
            "expiry": 3600,
            "channel_capacity": {
                "http.request": 200,
                "http.response*": 100,
            },
        },
        "ROUTING": "demo.routing.channel_routing",
    },
}

