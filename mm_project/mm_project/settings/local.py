from mm_project.settings import *
from decouple import config

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config('DB_NAME'),
        "USER": config('DB_USER'),
        "PASSWORD": config('DB_PASS'),
        "HOST": config('DB_HOST'),
        "PORT": config('DB_PORT')
    }
}

ALLOWED_HOSTS = ['https://young-peak-42669.herokuapp.com/', '127.0.0.1', '0.0.0.0']

