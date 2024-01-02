from pathlib import Path
import os
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-k+ru#e=^4c11xfold&^@js4tvlm=or#cwqyzca%hi=(+2wi4@v'

# DEBUG = True

# SECURITY WARNING: don't run with debug turned on in production!
if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bda',
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

ROOT_URLCONF = 'application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'bda/templates/Home'),
                 os.path.join(BASE_DIR, 'bda/templates/registration'),
                 os.path.join(BASE_DIR, 'bda/templates/dashboard'),
                 os.path.join(BASE_DIR, 'bda/templates/tspapp'),
                 os.path.join(BASE_DIR, 'bda/templates/product_category'),
                 os.path.join(BASE_DIR, 'bda/templates/product'),
                 os.path.join(BASE_DIR, 'bda/templates/supplier'),],
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

WSGI_APPLICATION = 'application.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'palp_main',
        'USER': 'tomal',  
        'PASSWORD': 'tomal1234',  
        'HOST': 'localhost',  
        'PORT': '3306',  
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'myapp/static')]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')


AUTH_USER_MODEL = 'bda.CustomUser'

LOGIN_URL = 'login'

#Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ftextrading@gmail.com'
EMAIL_HOST_PASSWORD = 'kqrovkgeaghpwluo'
DEFAULT_FROM_EMAIL = 'ftextrading@gmail.com'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
