# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
import random
from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from common.utils import send_templated_mail
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.auth.models import Group
from common.utils import send_sms


class UserManager(BaseUserManager):
    def create(self, mobile_no, password=None, **extra_fields):

        if not mobile_no:
            raise ValueError('User must have a mobile_no')

        user = self.model(
            mobile_no=mobile_no,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
      
        return user

    def create_superuser(self, mobile_no, password=None, **extra_fields):
        user = self.create(mobile_no, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(null=True, blank=True, unique=True)
    mobile_no = models.CharField(max_length=32, unique=True)
    mobile_no1 = models.CharField(max_length=32, null=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    user_type = models.ForeignKey('common.RespondentType', null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email_verification_code = models.CharField(
        max_length=128, null=True, blank=True)
    sms_verification_pin = models.IntegerField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_verified = models.BooleanField(default=False)
    dob = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    changed = models.DateTimeField(null=True, editable=False, auto_now=True)
    created = models.DateTimeField(
        null=True, editable=False, auto_now_add=True)
    opted_email = models.BooleanField(
        default=False, help_text="Opted in to receive emails")
    image = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=255, blank=True, null=True)
    fb_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    photos_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'mobile_no'

    def save(self, *args, **kwargs):
        # if not self.id:
        #     self.generate_sms_pin()
        #     self.send_otp()
        
        return super(User, self).save(*args, **kwargs)

    def generate_email_token(self):
        self.email_verification_code = uuid.uuid4().hex

    # def generate_sms_pin(self):
    #     pin = ''.join([str(random.choice(range(1, 9))) for i in range(5)])
    #     self.sms_verification_pin = int(pin)

    # def send_otp(self):
    #     msg = 'Your one time password for ILP is %s. Please enter this on our web page or mobile app to verify your mobile number.' % self.sms_verification_pin
    #     send_sms(self.mobile_no, msg)

    def get_token(self):
        return Token.objects.get(user=self).key

    def get_short_name(self):
        return self.first_name or ''

    def get_full_name(self):
        return ' '.join(
            filter(None, [self.first_name, self.last_name])) or self.email

    def send_verification_email(self):
        self.generate_email_token()
        url = reverse(
            'user_email_verify') + '?token={token}&email={email}'.format(
            token=self.email_verification_code,
            email=self.email
        )

        context = {
            'user': self,
            'site_url': Site.objects.get_current().domain,
            'url': url
        }

        send_templated_mail(
            from_email=settings.EMAIL_DEFAULT_FROM,
            to_emails=[self.email],
            subject='Please verify your email address',
            template_name='register',
            context=context
        )

        self.save()

    def __unicode__(self):
        return self.mobile_no


@receiver(post_save, sender=User)
def user_created_verify_email(sender, instance=None, created=False, **kwargs):
    if created and instance.email:
        instance.send_verification_email()

class UserBoundary(models.Model):
    user = models.ForeignKey('User')
    boundary = models.ForeignKey('boundary.Boundary')

    class Meta:
        unique_together = (('user', 'boundary'), )

''' This is specifically for django-guardian '''
def get_anonymous_user_instance(User):
    return User(first_name='Anonymous', last_name='Anonymous', mobile_no='00000000000')