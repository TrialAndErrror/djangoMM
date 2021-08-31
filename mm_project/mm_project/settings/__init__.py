"""
For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""


from .base import *
"""
All standard settings are contained within base.py, so we import that first.
"""


TESTING = False
"""
Set TESTING to True to allow for local testing of the site.
"""

if TESTING:
    """
    Because the Django manage.py does not support https, we have to disable SSL Redirect to allow for http traffic.
    We also enable debug for problem solving and disable some other cookie security and cross site scripting protection features.
    """
    DEBUG = True

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_BROWSER_XSS_FILTER = False
