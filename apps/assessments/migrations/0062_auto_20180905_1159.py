# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-05 06:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0061_auto_20180830_1205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questiongroupconcept',
            old_name='max_score',
            new_name='pass_score',
        ),
    ]
