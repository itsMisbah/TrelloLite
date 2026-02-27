# deploy_settings.py
from .settings import *
import os
import dj_database_url
from pathlib import Path

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

BASE_DIR = Path(__file__).resolve().parent.parent

# DEBUG = False
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# DATABASE
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Google OAuth
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.environ.get("CLIENT_ID"),
            'secret': os.environ.get("SECRET"),
            'key': ''
        }
    }
}

# Static + Media + WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']

# Email
# if os.environ.get('EMAIL_HOST'):
#     EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#     EMAIL_HOST = os.environ.get('EMAIL_HOST')
#     EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
#     EMAIL_USE_SSL = True
#     EMAIL_USE_TLS = False  
#     EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
#     EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
#     DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
# else:
#     EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'a3829e001@smtp-brevo.com'
EMAIL_HOST_PASSWORD = os.environ.get('BREVO_SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'misbahh77777@gmail.com'

