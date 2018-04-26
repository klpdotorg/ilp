# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-24 05:45
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(max_length=50)),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
    ]