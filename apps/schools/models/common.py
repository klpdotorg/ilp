from django.db import models

class AcademicYear(models.Model):
    """ Academic years in Schools """
    char_id = models.CharField(max_length=300, primary_key=True)
    year = models.CharField(max_length=10)
    active = models.ForeignKey('Status')


class Status(models.Model):
    """ Academic year status """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)


