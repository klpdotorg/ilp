from django.db import models
from users.models import User
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
    lang_name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    partner = models.ForeignKey('Partner', null=True)
    description = models.CharField(max_length=200, null=True)
    survey_on = models.ForeignKey('SurveyOnType')
    admin0 = models.ForeignKey('boundary.Boundary')
    status = models.ForeignKey('common.Status')
    image_required = models.NullBooleanField(default=False)

    class Meta:
        ordering = ['name', ]


class SurveyTagMapping(models.Model):
    """Association a tag with a survey"""
    survey = models.ForeignKey('Survey')
    tag = models.ForeignKey('SurveyTag')

    class Meta:
        unique_together = (('survey', 'tag'), )


class SurveyTagInstitutionMapping(models.Model):
    """Mapping Survey Tag to Insitutions in which it is active"""
    tag = models.ForeignKey('SurveyTag')
    institution = models.ForeignKey('schools.Institution')
    academic_year = models.ForeignKey('common.AcademicYear', null=True)

    class Meta:
        unique_together = (('tag', 'institution', 'academic_year'), )


class SurveyTagClassMapping(models.Model):
    """Mapping SurveyTag to list of classes"""
    tag = models.ForeignKey('SurveyTag')
    sg_name = models.CharField(max_length=20)
    academic_year = models.ForeignKey('common.AcademicYear', null=True)

    class Meta:
        unique_together = (('tag', 'sg_name', 'academic_year'), )


class QuestionGroup(models.Model):
    """Group of questions for a Survey"""
    name = models.CharField(max_length=100)
    lang_name = models.CharField(max_length=100, null=True)
    survey = models.ForeignKey('Survey')
    type = models.ForeignKey('SurveyType')
    inst_type = models.ForeignKey('common.InstitutionType')
    description = models.CharField(max_length=100, null=True)
    group_text = models.CharField(max_length=100, null=True)
    start_date = models.DateField(max_length=20)
    end_date = models.DateField(max_length=20, null=True)
    academic_year = models.ForeignKey('common.AcademicYear', null=True)
    version = models.IntegerField(blank=True, null=True)
    source = models.ForeignKey("Source", null=True)
    double_entry = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now, null=True)
    status = models.ForeignKey('common.Status')

    questions = models.ManyToManyField(
        'Question', through='Questiongroup_Questions'
    )


class Question(models.Model):
    """pool of questions"""
    question_text = models.CharField(max_length=300)
    display_text = models.CharField(max_length=300)
    lang_name = models.CharField(max_length=100, null=True)
    key = models.CharField(max_length=50, null=True)
    question_type = models.ForeignKey('QuestionType', null=True)
    options = models.CharField(max_length=300, null=True)
    is_featured = models.BooleanField()
    status = models.ForeignKey('common.Status')
    max_score = models.IntegerField(null=True)
    pass_score = models.CharField(max_length=100,null=True)


class Partner(models.Model):
    """Boundary that partner is associated with"""
    char_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    admin0 = models.ForeignKey('boundary.Boundary')


class Source(models.Model):
    """Different sources of information"""
    name = models.CharField(max_length=100)


class QuestionType(models.Model):
    """Different response and display choices for questions"""
    type = models.ForeignKey('ResponseType')
    display = models.ForeignKey('DisplayType')


class QuestionGroup_Questions(models.Model):
    """Mapping of questions to a question group"""
    questiongroup = models.ForeignKey('QuestionGroup')
    question = models.ForeignKey('Question')
    sequence = models.IntegerField(null=True)

    class Meta:
        unique_together = (('question', 'questiongroup'), )


class QuestionGroup_Institution_Association(models.Model):
    """Mapping of question group to different institutions
        for institution assessments"""
    institution = models.ForeignKey('schools.Institution')
    questiongroup = models.ForeignKey('QuestionGroup')
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('institution', 'questiongroup'), )


class QuestionGroup_StudentGroup_Association(models.Model):
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
