from django.db import models


class StudentReligion(models.Model):
    """ Model representing a student's religion """
    name = models.CharField(max_length=200)


class StudentCategory(models.Model):
    """ Model representing category of student """
    name = models.CharField(max_length=200)
