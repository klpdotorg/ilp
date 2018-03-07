from .survey import Survey, Question, Source, SurveyTag
from users.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class SurveyInstitutionAgg(models.Model):
    """Survey Institution Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    num_users = models.IntegerField(db_column="num_users")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_agg'


class SurveyBoundaryAgg(models.Model):
    """Survey Boundary Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    num_users = models.IntegerField(db_column="num_users")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_agg'


class SurveyElectionBoundaryAgg(models.Model):
    """Survey Election Boundary Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.ElectionBoundary', db_column="electionboundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    num_users = models.IntegerField(db_column="num_users")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_electionboundary_agg'


class SurveyBoundaryRespondentTypeAgg(models.Model):
    """Survey Boundary RespondentType Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    respondent_type = models.ForeignKey('common.RespondentType', db_column="respondent_type")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_respondenttype_agg'


class SurveyInstitutionRespondentTypeAgg(models.Model):
    """Survey RespondentType Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    respondent_type = models.ForeignKey('common.RespondentType', db_column="respondent_type")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_respondenttype_agg'


class SurveyBoundaryUserTypeAgg(models.Model):
    """Survey UserType Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    user_type = models.CharField(max_length=100, db_column="user_type")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_usertype_agg'


class SurveyInstitutionUserTypeAgg(models.Model):
    """Survey UserType Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    user_type = models.CharField(max_length=100, db_column="user_type")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_usertype_agg'


class SurveyBoundaryQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questionkey_agg'


class SurveyInstitutionQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questionkey_agg'


class SurveyBoundaryClassQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_questionkey_agg'


class SurveyInstitutionClassQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_questionkey_agg'


class SurveyBoundaryQuestionGroupQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_questionkey_agg'


class SurveyInstitutionQuestionGroupQuestionKeyAgg(models.Model):
    """Survey QuestionKey Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_key = models.CharField(max_length=100, db_column="question_key")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_questionkey_agg'


class SurveyBoundaryQuestionGroupGenderAgg(models.Model):
    """Survey QuestionGroup Gender Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_gender_agg'


class SurveyInstitutionQuestionGroupGenderAgg(models.Model):
    """Survey QuestionGroup Gender Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_gender_agg'


class SurveyBoundaryClassGenderAgg(models.Model):
    """Survey Class Gender Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_gender_agg'


class SurveyInstitutionClassGenderAgg(models.Model):
    """Survey Class Gender Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_gender_agg'


class SurveyBoundaryClassAnsAgg(models.Model):
    """Survey Class Answer Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    question_id = models.ForeignKey("Question", db_column="question_id")
    answer_option = models.CharField(max_length=100, db_column="answer_option")
    num_answers = models.IntegerField(db_column="num_answers")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_ans_agg'


class SurveyInstitutionClassAnsAgg(models.Model):
    """Survey Class Answer Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    yearmonth = models.IntegerField(db_column="yearmonth")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    question_id = models.ForeignKey("Question", db_column="question_id")
    answer_option = models.CharField(max_length=100, db_column="answer_option")
    num_answers = models.IntegerField(db_column="num_answers")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_ans_agg'


class SurveyBoundaryQuestionKeyCorrectAnsAgg(models.Model):
    """Survey QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questionkey_correctans_agg'


class SurveyInstitutionQuestionKeyCorrectAnsAgg(models.Model):
    """Survey QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questionkey_correctans_agg'


class SurveyClassQuestionKeyCorrectAnsAgg(models.Model):
    """Survey Class QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_class_questionkey_correctans_agg'


class SurveyBoundaryClassQuestionKeyCorrectAnsAgg(models.Model):
    """Survey Class QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_questionkey_correctans_agg'


class SurveyInstitutionClassQuestionKeyCorrectAnsAgg(models.Model):
    """Survey Class QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_questionkey_correctans_agg'


class SurveyQuestionGroupQuestionKeyCorrectAnsAgg(models.Model):
    """Survey QuestionGroup QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_questiongroup_questionkey_correctans_agg'


class SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg(models.Model):
    """Survey QuestionGroup QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_questionkey_correctans_agg'


class SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg(models.Model):
    """Survey QuestionGroup QuestionKey CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_questionkey_correctans_agg'


class SurveyQuestionGroupGenderCorrectAnsAgg(models.Model):
    """Survey QuestionGroup Gender CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_questiongroup_gender_correctans_agg'


class SurveyBoundaryQuestionGroupGenderCorrectAnsAgg(models.Model):
    """Survey QuestionGroup Gender CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_gender_correctans_agg'


class SurveyInstitutionQuestionGroupGenderCorrectAnsAgg(models.Model):
    """Survey QuestionGroup Gender CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_gender_correctans_agg'


class SurveyBoundaryQuestionGroupQuestionKeyGenderCorrectAns(models.Model):
    """Survey QuestionGroup QuestionKey Gender CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_questionkey_gender_correctans'


class SurveyInstitutionQuestionGroupQuestionKeyGenderCorrectAns(models.Model):
    """Survey QuestionGroup Gender CorrectAns Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    questiongroup_name = models.CharField(max_length=100, db_column="questiongroup_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_questionkey_gender_correct'


class SurveyClassGenderCorrectAnsAgg(models.Model):
    """Survey Class Gender Correct Ans Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_class_gender_correctans_agg'


class SurveyBoundaryClassGenderCorrectAnsAgg(models.Model):
    """Survey Class Gender Correct Ans Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_gender_correctans_agg'


class SurveyInstitutionClassGenderCorrectAnsAgg(models.Model):
    """Survey Class Gender Correct Ans Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_gender_correctans_agg'


class SurveyBoundaryClassQuestionKeyGenderCorrectAnsAgg(models.Model):
    """Survey Class Quesiton Key Gender Correct Ans Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_class_questionkey_gender_correctans_agg'


class SurveyInstitutionClassQuestionKeyGenderCorrectAnsAgg(models.Model):
    """Survey Class QuestionKey Gender Correct Ans Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    sg_name = models.CharField(max_length=100, db_column="sg_name")
    gender = models.ForeignKey("common.Gender", db_column="gender")
    question_key = models.CharField(max_length=100, db_column="question_key")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_class_questionkey_gender_correctans_agg'


class SurveyInstitutionQuestionAgg(models.Model):
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    question_key = models.CharField(max_length=100, db_column="question_key")
    question_id = models.ForeignKey('Question', db_column="question_id")
    question_desc = models.CharField(max_length=200, db_column="question_desc")
    score = models.BooleanField(db_column="score")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_question_agg'


class SurveyBoundaryQuestionGroupAnsAgg(models.Model):
    """Survey Answer Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_id = models.ForeignKey('Question', db_column="question_id")
    question_desc = models.CharField(max_length=200, db_column="question_desc")
    answer_option = models.CharField(max_length=100, db_column="answer_option")
    num_answers = models.IntegerField(db_column="num_answers")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_ans_agg'


class SurveyInstitutionQuestionGroupAnsAgg(models.Model):
    """Survey Answer Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    source = models.ForeignKey('Source', db_column="source")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_id = models.ForeignKey('Question', db_column="question_id")
    question_desc = models.CharField(max_length=200, db_column="question_desc")
    answer_option = models.CharField(max_length=100, db_column="answer_option")
    num_answers = models.IntegerField(db_column="num_answers")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_ans_agg'


class SurveyQuestionGroupAnsAgg(models.Model):
    """Survey Answer Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    question_id = models.ForeignKey('Question', db_column="question_id")
    question_desc = models.CharField(max_length=200, db_column="question_desc")
    answer_option = models.CharField(max_length=100, db_column="answer_option")
    num_answers = models.IntegerField(db_column="num_answers")

    class Meta:
        managed = False
        db_table = 'mvw_survey_questiongroup_ans_agg'


class SurveyInstitutionQuestionGroupAgg(models.Model):
    """Survey Institution QuestionGroup Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    institution_id = models.ForeignKey('schools.Institution', db_column="institution_id")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    num_users = models.IntegerField(db_column="num_users")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_institution_questiongroup_agg'


class SurveyBoundaryQuestionGroupAgg(models.Model):
    """Survey Boundary QuestionGroup Agg"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    questiongroup_id = models.ForeignKey('QuestionGroup', db_column="questiongroup_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    num_schools = models.IntegerField(db_column="num_schools")
    num_assessments = models.IntegerField(db_column="num_assessments")
    num_children = models.IntegerField(db_column="num_children")
    num_users = models.IntegerField(db_column="num_users")
    last_assessment = models.DateField(db_column="last_assessment")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_questiongroup_agg'


class SurveyTagMappingAgg(models.Model):
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    academic_year_id = models.ForeignKey('common.AcademicYear', db_column="academic_year_id")
    num_schools = models.IntegerField(db_column="num_schools")
    num_students = models.IntegerField(db_column="num_students")

    class Meta:
        managed = False
        db_table = 'mvw_survey_tagmapping_agg'


class SurveyBoundaryElectionTypeCount(models.Model):
    """Survey Boundary ElectionType Count"""
    survey_id = models.ForeignKey('Survey', db_column="survey_id")
    survey_tag = models.ForeignKey('SurveyTag', db_column="survey_tag")
    boundary_id = models.ForeignKey('boundary.Boundary', db_column="boundary_id")
    yearmonth = models.IntegerField(db_column="yearmonth")
    const_ward_type = models.ForeignKey('boundary.BoundaryType', db_column="const_ward_type")
    electionboundary_count = models.IntegerField(db_column="electionboundary_count")

    class Meta:
        managed = False
        db_table = 'mvw_survey_boundary_electiontype_count'
