import datetime
from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

SURVEY_TYPE = (
    ('assessment', 'Assessment'),
    ('perception', 'Perception'),
    ('monitor', 'Monitor'),
)

RESPONSE_TYPE = (
    ('text', 'Text'),
    ('score', 'Score'),
    ('boolean', 'Boolean'),
    ('grade', 'Grade'),
    ('choice_set', 'Choice_Set'),
)

DISPLAY_TYPE = (
    ('TextArea', 'TextArea'),
    ('TextBox', 'TextBox'),
    ('Radio', 'Radio'),
    ('Select', 'Select'),
    ('Checkbox', 'Checkbox'),
)

class Survey(models.Model):
    """Survey/Programme"""
    created_at = models.DateField(max_length=20)
    updated_at = models.DateField(max_length=20)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=SURVEY_TYPE)
    start_date = models.DateField(max_length=20,
                                 default=datetime.date.today())
    end_date = models.DateField(max_length=20, default="common.default_end_date")
    academic_year = models.ForeignKey('common.AcademicYear')
    partner = models.ForeignKey('Partner')
    inst_type = models.ForeignKey('common.InstitutionType')
    desc = models.CharField(max_length=200)
    status = models.ForeignKey('common.Status')


class QuestionGroup(models.Model):
    """Group of questions for a Survey"""
    verison = models.IntegerField(blank=True, null=True)
    source = models.ForeignKey("Source")
    start_date = models.DateField(max_length=20,
                                 default=datetime.date.today)
    end_date = models.DateField(max_length=20, default="common.default_end_date")
    name = models.CharField(max_length=100)
    created_at = models.DateField(max_length=20)
    updated_at = models.DateField(max_length=20)
    double_entry = models.BooleanField(default=True)
    survey = models.ForeignKey('Survey')
    created_by = models.ForeignKey(User)
    status = models.ForeignKey('common.Status')


class Question(models.Model):
    """pool of questions"""
    question_text = models.CharField(max_length=100)
    display_text = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    question_type = models.ForeignKey('QuestionType')
    options = models.CharField(max_length=100)
    is_featured = models.BooleanField()
    status = models.ForeignKey('common.Status')


class Partner(models.Model):
    """Boundary that partner is associated with"""
    name = models.CharField(max_length=100)
    admin0 = models.ForeignKey('boundary.Boundary')


class Source(models.Model):
    """Different sources of information"""
    name = models.CharField(max_length=100)


class QuestionType(models.Model):
    """Different response and display choices for questions"""
    type = models.CharField(max_length=20, choices=RESPONSE_TYPE)
    display = models.CharField(max_length=20, choices=DISPLAY_TYPE)


class QuestionGroupQuestions(models.Model):
    """Mapping of questions to a question group"""
    questiongroup = models.ForeignKey('QuestionGroup')
    question = models.ForeignKey('Question')
    sequence = models.IntegerField()

    class Meta:
        unique_together = (('question', 'questiongroup'), )


class QuestionGroupInstitutionAssociation(models.Model):
    """Mapping of question group to different institutions
        for institution assessments"""
    institution = models.ForeignKey('schools.Institution')
    questiongroup = models.ForeignKey('QuestionGroup')
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('institution', 'questiongroup'), )


class QuestionGroupStudentGroupAssociation(models.Model):
    """Mapping of student groups to question groups for student
        and studentgroup assessments"""
    studentgroup = models.ForeignKey('schools.StudentGroup')
    questiongroup = models.ForeignKey('QuestionGroup')
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('studentgroup', 'questiongroup'), )


class GuardianUserObjectPermission(models.Model):
    object_pk = models.CharField(max_length=100)
    content_type_id = models.ForeignKey(ContentType)
    user_id = models.ForeignKey(User)
    permission_id = models.ForeignKey(Permission)

