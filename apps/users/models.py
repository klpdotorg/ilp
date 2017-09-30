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
        # TODO: Uncomment the below line to encrypt the password
        # once users.User model is the default auth model
        # user.set_password(password)
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

    objects = UserManager()
    USERNAME_FIELD = 'email'
