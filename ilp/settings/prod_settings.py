DEBUG = False
# * is the least secure setting but it allows everyone to access. Tighten it
# to limit access
ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ilp2022',
        'USER': 'ilp',
        'PASSWORD': 'ilp',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}