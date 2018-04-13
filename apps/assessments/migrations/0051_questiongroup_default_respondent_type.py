# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-06 08:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_respondenttype_state_code'),
        ('assessments', '0050_questiongroup_respondenttype_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiongroup',
            name='default_respondent_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='common.RespondentType'),
        ),
    ]