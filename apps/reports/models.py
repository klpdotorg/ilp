from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Reports(models.Model):
    report_type = models.CharField(max_length=50)
    parameters = JSONField()
    
