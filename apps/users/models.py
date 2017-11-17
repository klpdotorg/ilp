# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser
)

from .choices import USER_TYPE_CHOICES


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(
            email=UserManager.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.password = password
        user.is_active = True
        user.save()
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    user_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    email_verification_code = models.CharField(max_length=128)
    sms_verification_pin = models.IntegerField()
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    dob = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    changed = models.DateTimeField(null=True, editable=False, auto_now=True)
    created = models.DateTimeField(
        null=True, editable=False, auto_now_add=True)
    opted_email = models.BooleanField(
        default=False, help_text="Opted in to receive emails")
    image = models.ImageField(upload_to='profile_pics', blank=True)
    about = models.TextField(blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    fb_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    photos_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
