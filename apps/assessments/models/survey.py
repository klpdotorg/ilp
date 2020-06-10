from users.models import User

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class SurveyType(models.Model):
    """Type of Survey"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class SurveyOnType(models.Model):
    """Type of entity survey is conducted on"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class ResponseType(models.Model):
    """Type of input expected"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class DisplayType(models.Model):
    """Display type to be used"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class SurveyTag(models.Model):
    """Tags to be used to group the Surveys"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class Survey(models.Model):
    """Survey/Programme"""
    name = models.CharField(max_length=100)
    lang_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    partner = models.ForeignKey('Partner', null=True, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=200, null=True, blank=True)
    survey_on = models.ForeignKey('SurveyOnType', on_delete=models.DO_NOTHING)
    admin0 = models.ForeignKey('boundary.Boundary', on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['name', ]


class SurveyTagMapping(models.Model):
    """Association a tag with a survey"""
    survey = models.ForeignKey('Survey', on_delete=models.DO_NOTHING)
    tag = models.ForeignKey('SurveyTag', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('survey', 'tag'), )


class SurveyTagInstitutionMapping(models.Model):
    """Mapping Survey Tag to Insitutions in which it is active"""
    tag = models.ForeignKey('SurveyTag',on_delete=models.DO_NOTHING)
    institution = models.ForeignKey('schools.Institution', on_delete=models.DO_NOTHING)
    academic_year = models.ForeignKey('common.AcademicYear', null=True, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('tag', 'institution', 'academic_year'), )


class SurveyTagClassMapping(models.Model):
    """Mapping SurveyTag to list of classes"""
    tag = models.ForeignKey('SurveyTag', on_delete=models.DO_NOTHING)
    sg_name = models.CharField(max_length=20)
    academic_year = models.ForeignKey('common.AcademicYear', null=True, on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('tag', 'sg_name', 'academic_year'), )


class SurveyUserTypeMapping(models.Model):
    """Association a survey with user types"""
    survey = models.ForeignKey('Survey', on_delete=models.DO_NOTHING)
    usertype = models.ForeignKey(
        'common.RespondentType', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('survey', 'usertype'), )


class QuestionGroup(models.Model):
    """Group of questions for a Survey"""
    name = models.CharField(max_length=100)
    lang_name = models.CharField(max_length=100, null=True, blank=True)
    survey = models.ForeignKey('Survey', on_delete=models.DO_NOTHING)
    type = models.ForeignKey('SurveyType', on_delete=models.DO_NOTHING)
    inst_type = models.ForeignKey(
        'common.InstitutionType', on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=100, null=True, blank=True)
    group_text = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(max_length=20)
    end_date = models.DateField(max_length=20, null=True, blank=True)
    academic_year = models.ForeignKey(
        'common.AcademicYear',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    version = models.IntegerField(blank=True, null=True)
    source = models.ForeignKey(
                                "Source",
                                null=True,
                                on_delete=models.DO_NOTHING)
    double_entry = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    status = models.ForeignKey(
                                'common.Status',
                                on_delete=models.DO_NOTHING)
    image_required = models.NullBooleanField(default=False)
    comments_required = models.NullBooleanField(default=False)
    respondenttype_required = models.NullBooleanField(default=False)
    default_respondent_type = models.ForeignKey(
                                                'common.RespondentType',
                                                null=True,
                                                on_delete=models.DO_NOTHING)
    max_score = models.IntegerField(null=True)

    questions = models.ManyToManyField(
        'Question', through='Questiongroup_Questions'
    )

    class Meta:
        permissions = (
            ('crud_answers', 'CRUD Answers'),
        )


class Concept(models.Model):
    char_id = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=50)


class MicroConceptGroup(models.Model):
    char_id = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=50)

class MicroConcept(models.Model):
    char_id = models.CharField(max_length=150, primary_key=True)
    description = models.CharField(max_length=150)


class QuestionLevel(models.Model):
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class QuestionInformationType(models.Model):
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class LearningIndicator(models.Model):
    char_id = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=50)


class Question(models.Model):
    """pool of questions"""
    question_text = models.CharField(max_length=300)
    display_text = models.CharField(max_length=300)
    lang_name = models.CharField(max_length=300, null=True, blank=True)
    key = models.CharField(max_length=50, null=True, blank=True)
    question_type = models.ForeignKey('QuestionType', null=True,
                                      on_delete=models.DO_NOTHING)
    options = models.CharField(max_length=750, null=True)
    lang_options = models.CharField(max_length=750, null=True)
    is_featured = models.BooleanField()
    status = models.ForeignKey('common.Status',
                               on_delete=models.DO_NOTHING)
    max_score = models.IntegerField(null=True)
    pass_score = models.CharField(max_length=100, null=True)
    concept = models.ForeignKey(
        'Concept',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    microconcept_group = models.ForeignKey(
        'MicroConceptGroup',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    microconcept = models.ForeignKey(
        'MicroConcept',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    question_level = models.ForeignKey(
        'QuestionLevel',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)# (beginner, intermediate and advanced) ,  i
    question_info_type = models.ForeignKey(
        'QuestionInformationType',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)# (abstract, comprehend, semi_abstract, visual), 
    learning_indicator = models.ForeignKey(
        'LearningIndicator',
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)#(analytical_skills, knowledge, understanding, application)
    


class QuestionGroupKey(models.Model):
    """question key information"""
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=50, null=True)
    max_score = models.IntegerField(null=True)


class QuestionGroupConcept(models.Model):
    """question key information"""
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    concept = models.CharField(max_length=50, null=True)
    microconcept_group = models.CharField(max_length=50, null=True)
    microconcept = models.CharField(max_length=150, null=True)
    pass_score = models.IntegerField(null=True)


class PartnerType(models.Model):
    """Type of partner"""
    char_id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=50)


class Partner(models.Model):
    """Boundary that partner is associated with"""
    char_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=100, null=True, blank=True)
    logo_file = models.CharField(max_length=50, null=True, blank=True)
    partner_type = models.ForeignKey(
        'PartnerType',
        default='primary',
        on_delete=models.DO_NOTHING)


class PartnerBoundaryMap(models.Model):
    """Mapping partner to boundary"""
    partner = models.ForeignKey('Partner', on_delete=models.DO_NOTHING)
    boundary = models.ForeignKey(
        'boundary.Boundary', on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('partner', 'boundary'), )


class Source(models.Model):
    """Different sources of information"""
    name = models.CharField(max_length=100)


class QuestionType(models.Model):
    """Different response and display choices for questions"""
    type = models.ForeignKey(
        'ResponseType',
        on_delete=models.DO_NOTHING)
    display = models.ForeignKey(
        'DisplayType',
        on_delete=models.DO_NOTHING)


class QuestionGroup_Questions(models.Model):
    """Mapping of questions to a question group"""
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    question = models.ForeignKey(
        'Question',
        on_delete=models.DO_NOTHING)
    sequence = models.IntegerField(null=True)

    class Meta:
        unique_together = (('question', 'questiongroup'), )


class QuestionGroup_Institution_Association(models.Model):
    """Mapping of question group to different institutions
        for institution assessments"""
    institution = models.ForeignKey(
        'schools.Institution',
        on_delete=models.DO_NOTHING)
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    status = models.ForeignKey(
        'common.Status',
        on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('institution', 'questiongroup'), )


class QuestionGroup_StudentGroup_Association(models.Model):
    """Mapping of student groups to question groups for student
        and studentgroup assessments"""
    studentgroup = models.ForeignKey(
        'schools.StudentGroup',
        on_delete=models.DO_NOTHING)
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    status = models.ForeignKey(
        'common.Status',
        on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('studentgroup', 'questiongroup'), )


class GuardianUserObjectPermission(models.Model):
    object_pk = models.CharField(max_length=100)
    content_type_id = models.ForeignKey(
        ContentType,
        on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING)
    permission_id = models.ForeignKey(
        Permission,
        on_delete=models.DO_NOTHING)


class CompetencyQuestionMap(models.Model):
    key = models.CharField(max_length=50, null=True, blank=True)
    lang_key = models.CharField(max_length=50, null=True, blank=True)
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    question = models.ForeignKey(
        'Question',
        on_delete=models.DO_NOTHING)
    max_score = models.IntegerField()

    class Meta:
        unique_together = (('questiongroup', 'question'), )


class CompetencyOrder(models.Model):
    key = models.CharField(max_length=50, null=True, blank=True)
    questiongroup = models.ForeignKey(
        'QuestionGroup',
        on_delete=models.DO_NOTHING)
    sequence = models.IntegerField()

    class Meta:
        unique_together = (('key', 'questiongroup'), )
