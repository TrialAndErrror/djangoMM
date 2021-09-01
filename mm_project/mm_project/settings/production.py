from .base import *
from .utils import load_config_data

CONFIG_PATH = f'./mm_project/settings/config_data.json'

config_data = load_config_data(CONFIG_PATH)

SECRET_KEY = config_data.get('SECRET_KEY')
DEBUG = bool(config_data.get('DEBUG', False))

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']

if config_data.get('ALLOWED_HOSTS', None):
    ALLOWED_HOSTS.extend(config_data['ALLOWED_HOSTS'])

DATABASES = {
    "default": config_data.get('default_db')
}

admin_list = config_data.get('ADMINS', None)
if admin_list:
    ADMINS = [tuple(item) for item in admin_list]


# HTTPS Settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SAMESITE = 'Strict'

SECURE_HSTS_SECONDS = 15768000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CSP_DEFAULT_SRC = ["'none'"]
CSP_SCRIPT_SRC = [
    "https://cdn.jsdelivr.net/",
    "'self'"
]
CSP_STYLE_SRC = ["'self'"]
CSP_IMG_SRC = ["'self'"]
CSP_FRAME_SRC = ["'none'"]

PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

SECURE_REFERRER_POLICY = "same-origin"