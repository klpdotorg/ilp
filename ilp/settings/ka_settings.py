from .base import *
from .prod_settings import *

ILP_STATE_ID = 'ka'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/states/' + ILP_STATE_ID, 'templates'],
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

#reports settings
GKA_SURVEY_ID=2
HOUSEHOLD_SURVEY_ID=11
HOUSEHOLD_QNGROUP_IDS=[18,20]
HOUSEHOLD_QUESTION_IDS=[269, 144, 145, 138]
