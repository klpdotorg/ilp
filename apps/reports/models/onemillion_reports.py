
from django.db import models
from django.contrib.postgres.fields import JSONField
from boundary.models import Boundary

def get_default_state():
    return 2

# Create your models here.
class Reports(models.Model):
    report_type = models.CharField(max_length=50)
    link_id = models.CharField(max_length=10,unique=True,null=True)
    parameters = JSONField()
    data = JSONField()
    state = models.ForeignKey('boundary.Boundary', db_column="state_id", default=get_default_state)

class Tracking(models.Model):
    report_id = models.ForeignKey('Reports', db_column="link_id")
    report_type = models.CharField(max_length=100, null=True)
    track_id = models.CharField(max_length=10)
    recipient = models.CharField(max_length=100,null=True)
    visit_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    visited_at = models.DateField(null=True)
    downloaded_at = models.DateField(null=True)
    status = models.CharField(max_length=10, null=True)
    role = models.CharField(max_length=20, null=True)
    created_at = models.DateField(auto_now=True,null=True)

    def __str__(self):
        return '{} sent to {}'.format(self.report_type, self.recipient)
