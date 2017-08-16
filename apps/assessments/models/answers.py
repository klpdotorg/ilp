from .survey import Question, QuestionGroup
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


EVENT_TYPE = (
    ("create", "Create"),
    ("update", "Update"),
    ("delete", "Delete"),
)


class AnswerInstitution(models.Model):
    """Answers for institution assessments"""
    institution = models.ForeignKey("schools.Institution")
    answer = models.CharField(max_length=200)
    question = models.ForeignKey("Question")
    questiongroup = models.ForeignKey("QuestionGroup")
    double_entry = models.IntegerField()
    created_by = models.ForeignKey(User, null=True)
    date_of_visit = models.DateField(max_length=20)
    respondent_type = models.ForeignKey("RespondentType", null=True)
    comments = models.CharField(max_length=200, null=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey("common.Status")
    sysid = models.IntegerField(null=True)
    entered_at = models.DateField(max_length=20)

    class Meta:
        unique_together = (('question', 'questiongroup', 'institution',
                            'date_of_visit'), )


class AnswerStudentGroup(models.Model):
    """Stores the answers of a survey for studentgroup"""
    studentgroup = models.ForeignKey("schools.StudentGroup")
    answer = models.CharField(max_length=200)
    question = models.ForeignKey("Question")
    questiongroup = models.ForeignKey("QuestionGroup")
    double_entry = models.IntegerField()
    created_by = models.ForeignKey(User, null=True)
    date_of_visit = models.DateField(max_length=20)
    respondent_type = models.ForeignKey("RespondentType", null=True)
    comments = models.CharField(max_length=200, null=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey("common.Status")

    class Meta:
        unique_together = (('question', 'questiongroup', 'studentgroup',
                            'date_of_visit'), )


class AnswerStudent(models.Model):
    """Stores the answers of a survey for student"""
    student = models.ForeignKey("schools.Student")
    answer = models.CharField(max_length=200)
    question = models.ForeignKey("Question")
    questiongroup = models.ForeignKey("QuestionGroup")
    double_entry = models.IntegerField()
    created_by = models.ForeignKey(User, null=True)
    date_of_visit = models.DateField(max_length=20)
    respondent_type = models.ForeignKey("RespondentType", null=True)
    comments = models.CharField(max_length=200, null=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey("common.Status")

    class Meta:
        unique_together = (('question', 'questiongroup', 'student'), )


class InstitutionImages(models.Model):
    """Images associated stories"""
    reponseid = models.ForeignKey("AnswerInstitution")
    image = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    filename = models.CharField(max_length=300)


class RespondentType(models.Model):
    name = models.CharField(max_length=100)


class EasyAuditCRUDEvent(models.Model):
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=100)
    object_json_repr = models.CharField(max_length=100)
    datetime = models.DateField(max_length=20)
    content_type_id = models.ForeignKey(ContentType)
    user_id = models.ForeignKey(User)
