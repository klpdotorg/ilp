# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-28 07:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0072_auto_20181205_0829'),
    ]

    operations = [
        migrations.AddField(
            model_name='competencyquestionmap',
            name='lang_key',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]