# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin

from .models import PreGroupUser, User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('mobile_no', 'first_name', 'last_name',)


admin.site.register(PreGroupUser)
admin.site.register(User, UserAdmin)