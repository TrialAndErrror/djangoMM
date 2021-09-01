from .base import *
from .utils import load_config_data

CONFIG_PATH = f'{BASE_DIR}/settings/test_config_data.json'

config_data = load_config_data(CONFIG_PATH)

SECRET_KEY = config_data.get('SECRET_KEY')
DEBUG = bool(config_data.get('DEBUG', True))

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']

if config_data.get('ALLOWED_HOSTS', None):
    ALLOWED_HOSTS.extend(config_data['ALLOWED_HOSTS'])

DATABASES = {
    "default": config_data.get('default_db')
}

admin_list = config_data.get('ADMINS', None)
if admin_list:
    ADMINS = [tuple(item) for item in admin_list]


SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False