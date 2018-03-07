from django.contrib.gis.db import models
from common.models import (AcademicYear)


class InstitutionAggregation(models.Model):
    """Data aggregation per institution"""
    institution = models.ForeignKey('Institution')
    institution_name = models.CharField(max_length=300, db_column="institution_name")
    academic_year = models.ForeignKey('common.AcademicYear')
    gender = models.ForeignKey('common.Gender', db_column="gender")
    mt = models.ForeignKey('common.Language', related_name='inst_agg_mt', db_column="mt")
    religion = models.ForeignKey('common.Religion', db_column="religion")
    inst_category = models.ForeignKey('common.StudentCategory', db_column="category")
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mvw_institution_aggregations'


class InstitutionStuGenderCount(models.Model):
    institution = models.ForeignKey('Institution')
    academic_year = models.ForeignKey('common.AcademicYear')
    num_boys = models.IntegerField(
        blank=True, null=True, db_column='num_boys')
    num_girls = models.IntegerField(
        blank=True, null=True, db_column='num_girls')

    class Meta:
        managed = False
        db_table = 'mvw_institution_stu_gender_count'


class InstitutionClassYearStuCount(models.Model):
    institution = models.ForeignKey('Institution', db_column="institution_id")
    studentgroup = models.CharField(max_length=300, db_column="studentgroup")
    academic_year = models.ForeignKey('common.AcademicYear', db_column="academic_year")
    num = models.IntegerField(blank=True, null=True, db_column='num')

    class Meta:
        managed = False
        db_table = 'mvw_institution_class_year_stucount'
