from common.models.choices import INSTITUTION_TYPE, INSTITUTION_GENDER
from django.contrib.gis.db import models


class InstitutionCategory(models.Model):
    """ Category for institution """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    institution_type = models.CharField(
        max_length=20, choices=INSTITUTION_TYPE)

class Management(models.Model):
    """ The school management """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)


class PinCode(models.Model):
    """ Pincodes """
    id = models.IntegerField(primary_key=True)
    geom = models.GeometryField()


class Institution(models.Model):
    """ An educational institution """
    id = models.IntegerField(primary_key=True)
    dise_code = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    category = models.ForeignKey('InstitutionCategory')
    gender = models.CharField(max_length=10, choices=INSTITUTION_GENDER)
    moi = models.ForeignKey('common.Language')
    institution_type = models.CharField(
        max_length=20, choices=INSTITUTION_TYPE)
    management = models.ForeignKey('Management')
    year_established = models.CharField(max_length=5, null=True, blank=True)
    rural_urban = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=1000)
    area = models.CharField(max_length=1000)
    village = models.CharField(max_length=1000)
    pincode = models.ForeignKey('PinCode')
    landmark = models.CharField(max_length=1000, null=True, blank=True)
    instidentification = models.CharField(
        max_length=1000, null=True, blank=True)
    instidentification2 = models.CharField(
        max_length=1000, null=True, blank=True)
    route_information = models.CharField(
        max_length=1000, null=True, blank=True)
    admin3 = models.ForeignKey('boundary.Boundary', related_name='institution_admin3')
    admin2 = models.ForeignKey('boundary.Boundary', related_name='institution_admin2')
    admin1 = models.ForeignKey('boundary.Boundary', related_name='institution_admin1')
    admin0 = models.ForeignKey('boundary.Boundary', related_name='institution_admin0')
    mp = models.ForeignKey('boundary.ElectionBoundary', related_name='institution_mp')
    mla = models.ForeignKey('boundary.ElectionBoundary', related_name='institution_mla')
    gp = models.ForeignKey('boundary.ElectionBoundary', related_name='institution_gp')
    ward = models.ForeignKey(
        'boundary.ElectionBoundary', related_name='institution_ward')
    coord = models.GeometryField()
    last_verified_year = models.ForeignKey('common.AcademicYear')
    status = models.ForeignKey('common.Status')
