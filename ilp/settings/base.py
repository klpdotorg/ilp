"""
Django settings for ilp project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'oj!h50gzzm1)!-znsv&fx2b6@#=bqxl3^i&lv6qqx5a$eu)74#'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

PROJECT_ROOT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.sites',
    'guardian',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_gis',
    'rest_framework_swagger',
    'django_extensions',
    'django_filters',
    'compressor',
    'easyaudit',
    'fixture_magic',
    # ILP apps
    'users',
    'common',
    'boundary',
    'schools',
    'dise',
    'assessments',
    'ivrs',
    'permissions',
    'reports'
)

# DRF Settings
LARGESETPAGINATION = 1000
REST_FRAMEWORK = {
    'PAGE_SIZE': 10,

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
        'permissions.permissions.IlpBasePermission',
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'common.renderers.ILPJSONRenderer',
        'common.renderers.KLPCSVRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ),

    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.ILPDefaultPagination',
}


# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',

]
DJANGO_EASY_AUDIT_WATCH_AUTH_EVENTS = False
DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False
DJANGO_EASY_AUDIT_REGISTERED_CLASSES = [
    'schools.Institution',
    'schools.StudentGroup',
    'schools.Student',
    'assessments.AnswerGroup_Institution',
    'assessments.AnswerInstitution',
    'assessments.AnswerGroup_Student',
    'assessments.AnswerStudent',
    'assessments.AnswerGroup_StudentGroup',
    'assessments.AnswerStudentGroup'
]
# Root URL Config
ROOT_URLCONF = 'ilp.urls'


# WSGI
WSGI_APPLICATION = 'ilp.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGES = (
    ('en', 'English'),
    ('kn', 'Kannada'),
    ('or', 'Odisha'),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

# Time zone
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True


# Authentication model
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailMobileUsernameBackend',
    'guardian.backends.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'assets', 'collected-static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets', 'static'),
)
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]


# Swagger
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    'JSON_EDITOR': True
}


# ILP SETTINGS
# This is the actual DISE academic year for which we're pulling data
DISE_ACADEMIC_YEAR = '16-17'
# This is just a variation of the above for front-end format purposes and
# DISE app endpoints.When the above changes, this also has to change
DISE_FRONTEND_ACADEMIC_YEAR = '16-17'
# This is the year KLP uses to query data in the DB
DEFAULT_ACADEMIC_YEAR = '1819'

DISE_API_BASE_URL = 'https://dise.dev.ilp.org.in/api/'

DISE_APP_URL = 'https://dise.dev.ilp.org.in/'

# Project 1 million related config settings
REPORTS_SERVER_BASE_URL = 'https://dev.ilp.org.in'


BLOG_FEED_URL = 'http://blog.klp.org.in/feeds/posts/default?alt=json'

EMAIL_DEFAULT_FROM = 'India Learning Partnership <dev@ilp.org.in>'

SERVER_EMAIL = 'no-reply@klp.org.in'

SITE_ID = 1

# We have to set this to None to get big file uploads from Konnect.
# For more information, please see this -
# https://docs.djangoproject.com/en/dev/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE = None

# Django-guardian settings
ANONYMOUS_USER_NAME = None

# Logging
LOG_ROOT = os.path.join(BASE_DIR, "/logs")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'development_logfile': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/django_dev.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR +'/django_production.log',
            'maxBytes' : 1024*1024*100, # 100MB
            'backupCount' : 5,
            'formatter': 'simple'
        },
        'dba_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false','require_debug_true'],
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': BASE_DIR + '/django_dba.log',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'schools': {
            'handlers': ['console','development_logfile'],
            'level': 'DEBUG',
            'propagate': True
         },
        'boundary': {
            'handlers': ['console','development_logfile'],
            'level': 'DEBUG',
            'propagate': True
        },
        'dba': {
            'handlers': ['dba_logfile'],
        },
        'django': {
            'handlers': ['development_logfile','production_logfile'],
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

