# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-15 07:47
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


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
                ('link_id', models.CharField(max_length=10, null=True, unique=True)),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.CharField(max_length=10)),
                ('visit_count', models.IntegerField()),
                ('download_count', models.IntegerField()),
                ('visited_at', models.DateField()),
                ('downloaded_at', models.DateField()),
                ('report_id', models.ForeignKey(db_column='link_id', on_delete=django.db.models.deletion.CASCADE, to='reports.Reports')),
            ],
        ),
    ]
