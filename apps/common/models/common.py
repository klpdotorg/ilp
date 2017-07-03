import datetime
import inspect
from enum import Enum
import sys
from django.db import models


class AcademicYear(models.Model):
    """ Academic years in Schools """
    char_id = models.CharField(max_length=300, primary_key=True)
    year = models.CharField(max_length=10)
    active = models.ForeignKey('Status')

    class Meta:
        unique_together = (('year'), )


class Status(models.Model):
    """ Status of the data"""
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class Language(models.Model):
    """ Languages used in School """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


def current_academic():
    ''' To select current academic year'''
    try:
        academicObj = AcademicYear.objects.get(active='AC')
        return academicObj
    except AcademicYear.DoesNotExist:
        return 1


def default_end_date():
    ''' To select academic year end date'''

    now = datetime.date.today()
    currentYear = int(now.strftime('%Y'))
    currentMont = int(now.strftime('%m'))
    academicYear = current_academic().name
    academicYear = academicYear.split('-')
    if currentMont > 5 and int(academicYear[0]) == currentYear:
        academic_end_date = datetime.date(currentYear+1, 5, 30)
    else:
        academic_end_date = datetime.date(currentYear, 5, 30)
    return academic_end_date


class InstitutionGender(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class InstitutionType(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class Gender(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class GroupType(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )

class Religion(models.Model):
    """Religion"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name


class StudentCategory(models.Model):
    """ Category of students"""
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s" % self.name
