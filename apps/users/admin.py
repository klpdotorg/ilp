# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.sites.models import Site

from rest_framework.authtoken.models import Token
from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent

from .models import PreGroupUser, User, Group

# Add PreGroupUser object so that program team members can
# add teachers/users of A3 app
admin.site.register(PreGroupUser)

# Unregister all unwanted models
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.unregister(Token)
admin.site.unregister(CRUDEvent)
admin.site.unregister(LoginEvent)
admin.site.unregister(RequestEvent)
