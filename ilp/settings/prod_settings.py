DEBUG = False
ALLOWED_HOSTS=['*']
DATABASES = {
    'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'ilpproduction',
    'USER': 'klp',
    'PASSWORD': 'klp',
    'HOST': 'localhost',
    'PORT': '5432',
    }
}

EXOTEL_SID = 'viamentis'
EXOTEL_TOKEN = '7de26f92f6a32731f39ad17fceedec161a61693a'
EXOTEL_SENDER_ID = 'KLPSMS'

DISE_API_BASE_URL = 'https://dise.staging.ilp.org.in/api/'
DISE_APP_URL = 'https://dise.staging.ilp.org.in/'
REPORTS_SERVER_BASE_URL = 'https://staging.ilp.org.in'

SLACK_URL = 'https://hooks.slack.com/services/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'

ADMINS = (
    ('Dev Team', 'dev@klp.org.in'),
)