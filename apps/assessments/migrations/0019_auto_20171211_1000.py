# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-11 04:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0018_auto_20171208_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerinstitution',
            name='answergroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='assessments.AnswerGroup_Institution'),
        ),
        migrations.AlterField(
            model_name='answerinstitution',
            name='double_entry',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
