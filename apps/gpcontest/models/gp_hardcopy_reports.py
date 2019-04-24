'''
This file contains the models for the GP contest hard copy report generation.
'''
from django.db import models
from boundary.models import ElectionBoundary
from assessments.models import QuestionGroup


class GPStudentScoreGroups(models.Model):
    gp_id = models.ForeignKey('boundary.ElectionBoundary', db_column="gp_id")
    questiongroup_id = models.ForeignKey('assessments.QuestionGroup',db_column="questiongroup_id")
    num_students = models.IntegerField(db_column="num_students")
    #<35%
    cat_a = models.IntegerField(db_column="cat_a")
    #BETWEEN 35 AND 60 %
    cat_b = models.IntegerField(db_column="cat_b")
    #BETWEEN 61 AND 75 %
    cat_c = models.IntegerField(db_column="cat_c")
    #BETWEEN 76 AND 100%
    cat_d = models.IntegerField(db_column="cat_d")

    class Meta:
        managed = False
        db_table = 'mvw_survey_eboundary_answers_agg'


class GPSchoolParticipationCounts(models.Model):
    gp_id = models.ForeignKey('boundary.ElectionBoundary', db_column="gp_id")
    num_schools = models.IntegerField(db_column="num_schools")

    class Meta:
        managed = False
        db_table = 'mvw_survey_eboundary_schoolcount_agg'


class GPInstitutionClassParticipationCounts(models.Model):
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    questiongroup_id = models.ForeignKey('assessments.QuestionGroup', db_column="questiongroup_id")
    num_students = models.IntegerField(db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_stucount_agg'
    
