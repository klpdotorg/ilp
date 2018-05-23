from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Reports(models.Model):
    report_type = models.CharField(max_length=50)
    link_id = models.CharField(max_length=10,unique=True,null=True)
    parameters = JSONField()
    data = JSONField()

class Tracking(models.Model):
    report_id = models.ForeignKey('Reports', db_column="link_id")
    track_id = models.CharField(max_length=10)
    visit_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    visited_at = models.DateField(null=True)
    downloaded_at = models.DateField(null=True)

class Sending_Information(models.Model):
    frequency = models.CharField(max_length=50) 
    contacts = models.CharField(max_length=50)
    parameters = JSONField()
    report_type = models.CharField(max_length=50) 
    
