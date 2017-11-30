from django.contrib.gis.db import models

from common.models import (Status, AcademicYear, Language,
                            Gender)

from schools.models import (Management, InstitutionCategory)

class BasicBoundaryAgg(models.Model):
    boundary = models.ForeignKey('Boundary', related_name="boundary_id", db_column="boundary_id")
    year = models.ForeignKey('common.AcademicYear', related_name="ac_year", db_column="ac_year")
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_basic_agg'


class BoundaryInstitutionGenderAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    year = models.ForeignKey('common.AcademicYear')
    gender = models.ForeignKey('common.Gender')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_gender_agg'

class BoundaryStudentMotherTongueAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    year = models.ForeignKey('common.AcademicYear')
    mt = models.ForeignKey('common.Language')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_mt_agg'

class BoundarySchoolCategoryAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    year = models.ForeignKey('common.AcademicYear')
    cat = models.ForeignKey('schools.InstitutionCategory')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_category_agg'

class BoundarySchoolManagementAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    year = models.ForeignKey('common.AcademicYear')
    management = models.ForeignKey('schools.Management')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_mgmt_agg'

class BoundarySchoolMoiAgg(models.Model):
    boundary = models.ForeignKey('Boundary')
    year = models.ForeignKey('common.AcademicYear')
    mt = models.ForeignKey('common.Language')
    num_schools = models.IntegerField(blank=True, null=True, db_column="num_schools")
    num_boys = models.IntegerField(blank=True, null=True, db_column="num_boys")
    num_girls = models.IntegerField(blank=True, null=True, db_column="num_girls")
    num_students = models.IntegerField(blank=True, null=True, db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_boundary_school_moi_agg'
