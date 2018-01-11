from django.contrib.gis.db import models

from common.models import (Status, AcademicYear, Language,
                            Gender)

from schools.models import (Management, InstitutionCategory)

class BasicBoundaryAgg(models.Model):
    boundary = models.ForeignKey('Boundary', related_name="boundary_id", db_column="boundary_id")
    year = models.ForeignKey('common.AcademicYear', related_name="ac_year", db_column="year")
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_basic_agg'


class BoundaryInstitutionGenderAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    gender_ac_year = models.ForeignKey('common.AcademicYear', related_name="gender_ac_year", db_column="year")
    gender = models.CharField(max_length=100, db_column="gender")
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_gender_agg'

class BoundaryStudentMotherTongueAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    mt_ac_year = models.ForeignKey('common.AcademicYear', related_name='mt_ac_year', db_column='year')
    mt = models.CharField(max_length=100, db_column='mt')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_student_mt_agg'

class BoundarySchoolCategoryAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    cat_ac_year = models.ForeignKey('common.AcademicYear', related_name='cat_ac_year', db_column='year')
    cat = models.CharField(max_length=100, db_column='category')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_category_agg'

class BoundarySchoolManagementAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    mgmt_ac_year = models.ForeignKey('common.AcademicYear', related_name='mgmt_ac_year', db_column='year')
    management = models.CharField(max_length=100, db_column='management')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_mgmt_agg'

class BoundarySchoolMoiAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    moi_ac_year = models.ForeignKey('common.AcademicYear', related_name='moi_ac_year', db_column='year')
    moi = models.CharField(max_length=100, db_column='moi')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_moi_agg'

