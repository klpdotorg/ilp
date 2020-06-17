from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


from assessments.models import QuestionGroup


class State(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    school_id = models.IntegerField(null=True, blank=True)
    answers = ArrayField(
            models.CharField(max_length=100, blank=True, null=True),
            null=True
    )
    date_of_visit = models.DateTimeField(default=timezone.now)
    telephone = models.CharField(max_length=50, blank=True)
    is_processed = models.BooleanField(default=False)
    is_invalid = models.BooleanField(default=False)
    qg_type = models.ForeignKey('QuestionGroupType', blank=True, null=True,
                                on_delete=models.DO_NOTHING)
    raw_data = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    user = models.ForeignKey('users.User', blank=True, null=True,
                             on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return str(self.date_of_visit) + " - " + str(self.qg_type.questiongroup.source.name)


class QuestionGroupType(models.Model):
    name = models.CharField(max_length=25)
    is_active = models.BooleanField(default=True)
    questiongroup = models.OneToOneField(QuestionGroup,on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return self.name


class IncomingNumber(models.Model):
    name = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    qg_type = models.ForeignKey(QuestionGroupType, blank=True, null=True,
                                on_delete=models.DO_NOTHING)

    def __unicode__(self):
        return self.qg_type.name + ":" + self.number


