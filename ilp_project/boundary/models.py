from django.contrib.gis.db import models


# Choices

INSTITUTION_GENDER = (
    ('boys', 'Boys'),
    ('girls', 'Girls'),
    ('co-ed', 'Co-Ed'),
)

INSTITUTION_TYPE = (
    ('pre', 'Pre'),
    ('primary', 'Primary'),
)


class InstitutionCategory(models.Model):
    """ Category for institution """
    name = models.CharField(max_length=300)
    institution_type = models.CharField(
        max_length=20, choices=INSTITUTION_TYPE)


class Language(models.Model):
    """ Languages used in School """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)


class Management(models.Model):
    """ The school management """
    name = models.CharField(max_length=300)


class Status(models.Model):
    """ Academic year status """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)


class AcademicYear(models.Model):
    """ Academic years in Schools """
    char_id = models.CharField(max_length=300, primary_key=True)
    year = models.CharField(max_length=10)
    active = models.ForeignKey(Status)


class PinCode(models.Model):
    """ Pincodes """
    geom = models.GeometryField()
