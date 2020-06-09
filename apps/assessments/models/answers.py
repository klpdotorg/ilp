from .survey import Question, QuestionGroup
from common.models import RespondentType
from users.models import User
from django.db import models
from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


EVENT_TYPE = (
    ("create", "Create"),
    ("update", "Update"),
    ("delete", "Delete"),
)


class AnswerGroup_Institution(models.Model):
    """Stores common value for the answers to a particular QuestionGroup for a
    group value"""
    institution = models.ForeignKey(
        "schools.Institution",
        on_delete=models.DO_NOTHING)
    questiongroup = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.DO_NOTHING)
    group_value = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.DO_NOTHING)
    date_of_visit = models.DateTimeField(default=timezone.now)
    respondent_type = models.ForeignKey(
        RespondentType,
        null=True,
        on_delete=models.DO_NOTHING)
    comments = models.CharField(max_length=2000, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey(
        "common.Status",
        on_delete=models.DO_NOTHING)
    sysid = models.IntegerField(null=True)
    entered_at = models.DateTimeField(default=timezone.now, null=True)
    location = models.GeometryField(null=True)
    mobile = models.CharField(max_length=32, null=True)


class AnswerInstitution(models.Model):
    """Answers for institution assessments"""
    answergroup = models.ForeignKey(
        "AnswerGroup_Institution",
        related_name="answers",
        on_delete=models.DO_NOTHING)
    question = models.ForeignKey(
        "Question",
        on_delete=models.DO_NOTHING)
    answer = models.CharField(max_length=200)
    double_entry = models.IntegerField(null=True,default=0)

    class Meta:
        unique_together = (('answergroup', 'question'), )


class AnswerGroup_StudentGroup(models.Model):
    """Stores common value for the answers to a particular QuestionGroup for a
    group value"""
    studentgroup = models.ForeignKey(
        "schools.StudentGroup",
        on_delete=models.DO_NOTHING)
    questiongroup = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.DO_NOTHING)
    group_value = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.DO_NOTHING)
    date_of_visit = models.DateTimeField(default=timezone.now)
    respondent_type = models.ForeignKey(
        RespondentType,
        null=True,
        on_delete=models.DO_NOTHING)
    comments = models.CharField(max_length=2000, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey(
        "common.Status",
        on_delete=models.DO_NOTHING)
    location = models.GeometryField(null=True)
    mobile = models.CharField(max_length=32, null=True)
    entered_at = models.DateTimeField(default=timezone.now, null=True)


class AnswerStudentGroup(models.Model):
    """Answers for studentgroup assessments"""
    answergroup = models.ForeignKey(
        "AnswerGroup_StudentGroup",
        on_delete=models.DO_NOTHING)
    question = models.ForeignKey(
        "Question",
        on_delete=models.DO_NOTHING)
    answer = models.CharField(max_length=200)
    double_entry = models.IntegerField(null=True)

    class Meta:
        unique_together = (('answergroup', 'question'), )


class AnswerGroup_Student(models.Model):
    """Stores common value for the answers to a particular QuestionGroup for a
    group value"""
    student = models.ForeignKey(
        "schools.Student",
        on_delete=models.DO_NOTHING)
    questiongroup = models.ForeignKey(
        "QuestionGroup",
        on_delete=models.DO_NOTHING)
    group_value = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING)
    date_of_visit = models.DateTimeField(default=timezone.now)
    respondent_type = models.ForeignKey(
        RespondentType,
        null=True,
        on_delete=models.DO_NOTHING)
    comments = models.CharField(max_length=2000, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    status = models.ForeignKey("common.Status",on_delete=models.DO_NOTHING)
    location = models.GeometryField(null=True)
    mobile = models.CharField(max_length=32, null=True)
    entered_at = models.DateTimeField(default=timezone.now, null=True)


class AnswerStudent(models.Model):
    """Answers for studentgroup assessments"""
    answergroup = models.ForeignKey(
        "AnswerGroup_Student", on_delete=models.DO_NOTHING)
    question = models.ForeignKey("Question", on_delete=models.DO_NOTHING)
    answer = models.CharField(max_length=200)
    double_entry = models.IntegerField(null=True)

    class Meta:
        unique_together = (('answergroup', 'question'), )


class InstitutionImages(models.Model):
    """Images associated stories"""
    answergroup = models.ForeignKey(
        "AnswerGroup_Institution",on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to='sys_images')
    is_verified = models.BooleanField(default=False)
    filename = models.CharField(max_length=300)

    def __unicode__(self):
        return "{}: {}".format(self.story.name, self.image)


class EasyAuditCRUDEvent(models.Model):
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=100)
    object_json_repr = models.CharField(max_length=100)
    datetime = models.DateTimeField(default=timezone.now)
    content_type_id = models.ForeignKey(
        ContentType,
        on_delete=models.DO_NOTHING)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)
