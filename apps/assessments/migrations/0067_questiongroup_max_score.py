# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-10-17 03:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0066_surveyeboundaryqdetailsagg_surveyeboundaryqdetailscorrectansagg_surveyeboundaryquestiongroupagg_surv'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiongroup',
            name='max_score',
            field=models.IntegerField(null=True),
        ),
    ]
