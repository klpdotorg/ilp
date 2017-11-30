import json

from django.contrib.gis.db import models

from common.models import (Status, AcademicYear)
from django.conf import settings


class InstitutionCategory(models.Model):
    """ Category for institution """
    name = models.CharField(max_length=300)
    institution_type = models.ForeignKey('common.InstitutionType')

    def __unicode__(self):
        return "%s" % self.name


class Management(models.Model):
    """ The school management """
    name = models.CharField(max_length=300)

    def __unicode__(self):
        return "%s" % self.name


class PinCode(models.Model):
    """ Pincodes """
    geom = models.GeometryField()

    def __unicode__(self):
        return "%s" % self.geom


class Institution(models.Model):
    """ An educational institution """
    dise = models.ForeignKey('dise.BasicData', null=True, blank=True)
    name = models.CharField(max_length=300)
    category = models.ForeignKey('InstitutionCategory')
    gender = models.ForeignKey('common.InstitutionGender')
    institution_type = models.ForeignKey('common.InstitutionType')
    management = models.ForeignKey('Management')
    year_established = models.CharField(max_length=5, null=True, blank=True)
    rural_urban = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)
    area = models.CharField(max_length=1000, null=True, blank=True)
    village = models.CharField(max_length=1000, null=True, blank=True)
    pincode = models.ForeignKey('PinCode', null=True, blank=True)
    landmark = models.CharField(max_length=1000, null=True, blank=True)
    instidentification = models.CharField(
        max_length=1000, null=True, blank=True)
    instidentification2 = models.CharField(
        max_length=1000, null=True, blank=True)
    route_information = models.CharField(
        max_length=1000, null=True, blank=True)
    admin3 = models.ForeignKey(
        'boundary.Boundary', related_name='institution_admin3')
    admin2 = models.ForeignKey(
        'boundary.Boundary', related_name='institution_admin2')
    admin1 = models.ForeignKey(
        'boundary.Boundary', related_name='institution_admin1')
    admin0 = models.ForeignKey(
        'boundary.Boundary', related_name='institution_admin0')
    mp = models.ForeignKey(
        'boundary.ElectionBoundary', related_name='institution_mp', null=True)
    mla = models.ForeignKey(
        'boundary.ElectionBoundary', related_name='institution_mla', null=True)
    gp = models.ForeignKey(
        'boundary.ElectionBoundary', related_name='institution_gp', null=True)
    ward = models.ForeignKey(
        'boundary.ElectionBoundary', related_name='institution_ward',
        null=True)
    coord = models.GeometryField(null=True)
    last_verified_year = models.ForeignKey('common.AcademicYear', null=True)
    status = models.ForeignKey(
        'common.Status', default=Status.ACTIVE)

    def get_geometry(self):
        if hasattr(self, 'coord') and self.coord is not None:
            return json.loads(self.coord.geojson)
        else:
            return {}
    
    def get_mt_profile(self):
        profile = {}
        aggregation = self.institutionaggregation_set.filter(academic_year=settings.DEFAULT_ACADEMIC_YEAR)
        # print("Inside institution model, printing inst aggregation",# aggregation)
        for agg in aggregation:
            if agg.mt in profile:
                profile[agg.mt.name] += agg.num
            else:
                profile[agg.mt.name] = agg.num
        # print("Profile is: ", profile)
        return profile


    class Meta:
        unique_together = (('name', 'dise', 'admin3'), )

    def __unicode__(self):
        return "%s" % self.name


class InstitutionLanguage(models.Model):
    institution = models.ForeignKey(
        'Institution', related_name='institution_languages')
    moi = models.ForeignKey('common.Language')

    class Meta:
        unique_together = (('institution', 'moi'), )



