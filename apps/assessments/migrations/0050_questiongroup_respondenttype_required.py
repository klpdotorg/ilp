# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-21 03:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0049_auto_20180316_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiongroup',
            name='respondenttype_required',
            field=models.NullBooleanField(default=False),
        ),
    ]