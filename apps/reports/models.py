from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Reports(models.Model):
    report_type = models.CharField(max_length=50)
    link_id = models.CharField(max_length=10,unique=True,null=True)
    parameters = JSONField()


class Tracking(models.Model):
    report_id = models.ForeignKey('Reports', db_column="link_id")
    track_id = models.CharField(max_length=10)
    visit_count = models.IntegerField()
    download_count = models.IntegerField()
    visited_at = models.DateField()
    downloaded_at = models.DateField()
    
