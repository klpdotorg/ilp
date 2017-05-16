# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 06:26
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('char_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('year', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('institution_type', models.CharField(choices=[('pre', 'Pre'), ('primary', 'Primary')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('char_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Management',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='PinCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('char_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.AddField(
            model_name='academicyear',
            name='active',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundary.Status'),
        ),
    ]
