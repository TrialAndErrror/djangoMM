import os
from pathlib import Path

from mm_project.settings.utils import Config, HTTPSSettings

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.yml"

"""
Load config data from json file.
"""
config_data = Config.from_yaml(CONFIG_PATH)
if config_data is None:
    raise Exception('Config data not found; please fix any config errors and restart the application')

SECRET_KEY = config_data.secret_key
DEBUG = config_data.debug
ALLOWED_HOSTS = config_data.allowed_hosts

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    "frontend",
    "api",
    'accounts',
    'bills',
    'expenses',
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap5",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mm_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mm_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config_data.db_settings.name,
        "USER": config_data.db_settings.user,
        "PASSWORD": config_data.db_settings.password,
        "HOST": "db",
        "PORT": "5432"
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'login'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

ADMINS = config_data.admins

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# HTTPS Settings
if config_data.https_settings:
    https_settings: HTTPSSettings = config_data.https_settings
    SESSION_COOKIE_SECURE = https_settings.session_cookie_secure
    CSRF_COOKIE_SECURE = https_settings.csrf_cookie_secure
    SECURE_SSL_REDIRECT = https_settings.secure_ssl_redirect
    SECURE_BROWSER_XSS_FILTER = https_settings.secure_browser_xss_filter
    SESSION_COOKIE_SAMESITE = https_settings.session_cookie_samesite

    SECURE_HSTS_SECONDS = https_settings.secure_hsts_seconds
    SECURE_HSTS_INCLUDE_SUBDOMAINS = https_settings.secure_hsts_include_subdomains
    SECURE_HSTS_PRELOAD = https_settings.secure_hsts_preload

    SECURE_CONTENT_TYPE_NOSNIFF = https_settings.secure_content_type_nosniff
    X_FRAME_OPTIONS = https_settings.x_frame_options

    CSP_DEFAULT_SRC = https_settings.csp_default_src
    CSP_SCRIPT_SRC = https_settings.csp_script_src

    CSP_STYLE_SRC = https_settings.csp_style_src
    CSP_IMG_SRC = https_settings.csp_img_src
    CSP_FRAME_SRC = https_settings.csp_frame_src

    PERMISSIONS_POLICY = https_settings.permissions_policy

    SECURE_REFERRER_POLICY = https_settings.secure_referrer_policy