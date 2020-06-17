from django.contrib.gis.db import models
from common.models import (AcademicYear)


class InstitutionAggregation(models.Model):
    """Data aggregation per institution"""
    institution = models.ForeignKey('Institution', on_delete=models.DO_NOTHING)
    institution_name = models.CharField(
        max_length=300, db_column="institution_name")
    academic_year = models.ForeignKey(
        'common.AcademicYear', on_delete=models.DO_NOTHING)
    gender = models.ForeignKey(
        'common.Gender', db_column="gender", on_delete=models.DO_NOTHING)
    mt = models.ForeignKey('common.Language', related_name='inst_agg_mt',
                           db_column="mt", on_delete=models.DO_NOTHING)
    religion = models.ForeignKey(
        'common.Religion', db_column="religion", on_delete=models.DO_NOTHING)
    inst_category = models.ForeignKey(
        'common.StudentCategory', db_column="category", on_delete=models.DO_NOTHING)
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mvw_institution_aggregations'


class InstitutionStuGenderCount(models.Model):
    institution = models.ForeignKey('Institution', on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey(
        'common.AcademicYear', on_delete=models.DO_NOTHING)
    num_boys = models.IntegerField(
        blank=True, null=True, db_column='num_boys')
    num_girls = models.IntegerField(
        blank=True, null=True, db_column='num_girls')

    class Meta:
        managed = False
        db_table = 'mvw_institution_stu_gender_count'


class InstitutionClassYearStuCount(models.Model):
    institution = models.ForeignKey(
        'Institution', db_column="institution_id", on_delete=models.DO_NOTHING)
    studentgroup = models.CharField(max_length=300, db_column="studentgroup")
    academic_year = models.ForeignKey(
        'common.AcademicYear', db_column="academic_year", on_delete=models.DO_NOTHING)
    num = models.IntegerField(blank=True, null=True, db_column='num')

    class Meta:
        managed = False
        db_table = 'mvw_institution_class_year_stucount'
