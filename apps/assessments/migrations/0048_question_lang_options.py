# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-15 03:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0047_auto_20180307_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='lang_options',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
