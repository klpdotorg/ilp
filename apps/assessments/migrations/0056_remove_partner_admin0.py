# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-07-10 08:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0055_auto_20180709_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partner',
            name='admin0',
        ),
    ]
