"""
Django settings for doctors_appointment project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-v$zu3k_g_p2dp_!2*hw!m1w2%dsl@q#&uld&7ad(wzdv#u=#*^'
DEBUG = True
ALLOWED_HOSTS = ["0.0.0.0","127.0.0.1", "localhost", "20.20.20.8", "192.168.1.151","192.168.8.167","192.168.8.177","192.168.8.178","192.168.8.175"]

INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'hospitals',
    'doctors',
    'patients',
    'bookings',
    'payments',
    'notifications',
    'reports',
    'reviews',
    'dashboard',
    'home',
    'blog',
    'hospital_staff',
    'advertisements',
    'menu_generator',
    'ckeditor',
    'widget_tweaks',
    'rolepermissions',
    'api',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
    'rest_framework',
    'rest_framework_simplejwt',
]




REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '100/minute'
    },
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,



}
    #'EXCEPTION_HANDLER': '/api/handle.py'



from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    # Serializers
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.RoleBasedAccessMiddleware',
]


ROOT_URLCONF = 'doctors_appointment.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications',
                'users.context_processors.admin_user_context',
            ],
        },
    },
]


WSGI_APPLICATION = 'doctors_appointment.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'doctor_appointment'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'",
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True,
            'isolation_level': 'read committed',
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION',
        }
    }
}

DATABASE_OPTIONS = {
    'timeout': 20,
    'connect_timeout': 10,
}


    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }


AUTH_USER_MODEL='users.CustomUser'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [

]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)


STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, '/static')



STATICFILES_DIRS = [os.path.join(BASE_DIR, 'doctors_appointment/static')]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


####################################################################################
# Example: settings.py
####################################################################################

NAV_MENU_TOP = [
    {
        "name": "الرئيسية",
        "url": "/",
    },
    {
        "name": "المستشفيات",
        "url": "/hospitals/all/",
    },
    {
        "name": "الأطباء",
        "url": "/search/",
    },
     {
        "name": "المدونة",
        "url": "/blog/",
    },
    {
        "name": "الأسئلة الشائعة",
        "url": "/faq",
    },
    {
        "name": "من نحن",
        "url": "/about",
    },
    
    {
        "name": "المزيد",
        "url": "/",

        "submenu": [
        #     {
        #     "name": "من نحن",
        #     "url": "/about/",
        # },
            # {
            #     "name": "اتصل بنا",
            #     "url": "/",

            # },
            {
                "name": "الشروط والأحكام",
                "url": "/terms-condition",

            },
            {
                "name": "سياسة الخصوصية",
                "url": "/privacy-policy",

            }
        ],
        
    },
   
]


FOOTER_MENU_ONE = [
    {
        "name": "Contact Us",
    },
]

FOOTER_MENU_RIGHT = [
    {
        "name": "Address",
        "url": "/address",
    },
]


CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList',
            'blockQuote', 'undo', 'redo'
        ],
        'language': 'en',
    },
}


# إعدادات Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'UTC'
