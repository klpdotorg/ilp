'''
This file contains the models for the GP contest hard copy report generation.
GP Contest reports use materialized views throughout and not actual tables.
Most of the logic in computation resides in the materialized view scripts, NOT
in Python code. Materialized views should be run first before running the 
report generation code.
'''
from django.db import models
from boundary.models import ElectionBoundary
from assessments.models import QuestionGroup


class GPStudentScoreGroups(models.Model):
    """
    Materialized view that captures number of students who scored in various
    categories at a grade level in schools.
    """
    gp_id = models.ForeignKey('boundary.ElectionBoundary', db_column="gp_id")
    questiongroup_id = models.ForeignKey(
        'assessments.QuestionGroup',
        db_column="questiongroup_id")
    num_students = models.IntegerField(db_column="num_students")
    # <35%
    cat_a = models.IntegerField(db_column="cat_a")
    # BETWEEN 35 AND 60 %
    cat_b = models.IntegerField(db_column="cat_b")
    # BETWEEN 61 AND 75 %
    cat_c = models.IntegerField(db_column="cat_c")
    # BETWEEN 76 AND 100%
    cat_d = models.IntegerField(db_column="cat_d")

    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_eboundary_answers_agg'


class GPSchoolParticipationCounts(models.Model):
    """
    Materialized view to show school participation in a GP contest in a given
    time frame
    """
    gp_id = models.ForeignKey('boundary.ElectionBoundary', db_column="gp_id")
    num_schools = models.IntegerField(db_column="num_schools")

    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_eboundary_schoolcount_agg'


class GPInstitutionClassParticipationCounts(models.Model):
    """
    Materialized view to show student counts per class for each school in
    a given time frame
    """
    institution_id = models.ForeignKey(
        'schools.Institution',
        db_column="institution_id")
    questiongroup_id = models.ForeignKey(
        'assessments.QuestionGroup',
        db_column="questiongroup_id")
    num_students = models.IntegerField(db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_institution_stucount_agg'


class GPInstitutionClassQDetailsAgg(models.Model):
    """ Model on the materialized view to return questions per class
    and associated correct answers and percentage scores PER GRADE in a school 
    """
    institution_id = models.ForeignKey(
                                    'schools.Institution',
                                    db_column="institution_id")
    questiongroup_id = models.ForeignKey(
                            'assessments.QuestionGroup',
                            db_column="questiongroup_id")
    microconcept = models.ForeignKey(
        'assessments.MicroConcept',
        db_column="microconcept_id")
    total_answers = models.IntegerField(db_column="total_answers")
    correct_answers = models.IntegerField(db_column="correct_answers")
    percent_score = models.FloatField(db_column="percent_score")
    question_id = models.ForeignKey('assessments.Question', db_column="question_id")
    question_sequence = models.IntegerField(db_column="question_sequence")
    question_local_lang_text = models.CharField(db_column="question_lang_name",max_length=200)

    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_institution_qdetails_percentages_agg'


class GPInstitutionDeficientCompetencyPercentagesAgg(models.Model):
    institution_id = models.ForeignKey(
                                    'schools.Institution',
                                    db_column="institution_id")
    questiongroup_id = models.ForeignKey(
                            'assessments.QuestionGroup',
                            db_column="questiongroup_id")
    question_key = models.CharField(max_length=100, db_column="question_key")
    lang_question_key = models.CharField(max_length=100,
                                         db_column="lang_question_key")
    total_answers = models.IntegerField(db_column="total_answers")
    correct_answers = models.IntegerField(db_column="correct_answers")
    percent_score = models.FloatField(db_column="percent_score")
    
    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_concept_percentages_agg'


class GPContestSchoolDetails(models.Model):
    institution_id = models.ForeignKey('schools.Institution',
                            db_column="institution_id")
    institution_name = models.CharField(max_length=200,
                                        db_column="institution_name")
    school_code = models.IntegerField(db_column="dise_code")
    district_name = models.CharField(max_length=150,
                                     db_column="district_name")
    block_name = models.CharField(
                                    max_length=150,
                                    db_column="block_name")
    cluster_name = models.CharField(
                                    max_length=150,
                                    db_column="cluster_name")
    gp_id = models.ForeignKey('boundary.ElectionBoundary', db_column="gp_id")
    gp_name = models.CharField(max_length=150, db_column="gp_name")

    class Meta:
        managed = False
        db_table = 'mvw_gpcontest_school_details'

