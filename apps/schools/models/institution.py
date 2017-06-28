from django.contrib.gis.db import models


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
    dise_code = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    category = models.ForeignKey('InstitutionCategory')
    gender = models.ForeignKey('common.Gender')
    moi = models.ForeignKey('common.Language')
    institution_type = models.ForeignKey('common.InstitutionType')
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
            'boundary.ElectionBoundary', related_name='institution_ward', null=True)
    coord = models.GeometryField(null=True)
    last_verified_year = models.ForeignKey('common.AcademicYear', null=True)
    status = models.ForeignKey('common.Status')

    class Meta:
        unique_together = (('dise_code'), )

    def __unicode__(self):
        return "%s" % self.name
