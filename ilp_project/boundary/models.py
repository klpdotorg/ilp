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
    active = models.ForeignKey('Status')


class PinCode(models.Model):
    """ Pincodes """
    id = models.IntegerField(primary_key=True)
    geom = models.GeometryField()


class BoundaryType(models.Model):
    """ Boundary type """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)


class Boundary(models.Model):
    """ Regional boundaries """
    parent = models.ForeignKey('self')
    name = models.CharField(max_length=300)
    boundary_type = models.ForeignKey('BoundaryType')
    institution_type = models.CharField(
        max_length=20, choices=INSTITUTION_TYPE)
    dise_slug = models.CharField(max_length=300)
    geom = models.GeometryField()
    status = models.ForeignKey('Status')


class ElectionBoundary(models.Model):
    """ Election boundaries """
    state = models.ForeignKey('self')
    dise_slug = models.CharField(max_length=300)
    elec_comm_code = models.IntegerField()
    const_ward_name = models.CharField(max_length=300)
    const_ward_type = models.ForeignKey('BoundaryType')
    current_elected_rep = models.CharField(max_length=300)
    current_elected_party = models.ForeignKey('ElectionParty')
    status = models.ForeignKey('Status')


class BoundaryNeighbours(models.Model):
    boundary = models.ForeignKey('Boundary')
    neighbour = models.ForeignKey('ElectionBoundary')


class ElectionNeighbours(models.Model):
    elect_boundary = models.ForeignKey('ElectionBoundary')
    neighbour = models.ForeignKey(
        'ElectionBoundary', related_name='election_neighbour_neighbour')


class ElectionParty(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    elect_boundary = models.ForeignKey('ElectionBoundary')
    neighbour = models.ForeignKey(
        'ElectionBoundary', related_name='election_party_neighbour')


class Institution(models.Model):
    """ An educational institution """
    dise_code = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    category = models.ForeignKey('InstitutionCategory')
    gender = models.CharField(max_length=10, choices=INSTITUTION_GENDER)
    moi = models.ForeignKey('Language')
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
    admin3 = models.ForeignKey('Boundary', related_name='institution_admin3')
    admin2 = models.ForeignKey('Boundary', related_name='institution_admin2')
    admin1 = models.ForeignKey('Boundary', related_name='institution_admin1')
    admin0 = models.ForeignKey('Boundary', related_name='institution_admin0')
    mp = models.ForeignKey('ElectionBoundary', related_name='institution_mp')
    mla = models.ForeignKey('ElectionBoundary', related_name='institution_mla')
    gp = models.ForeignKey('ElectionBoundary', related_name='institution_gp')
    ward = models.ForeignKey(
        'ElectionBoundary', related_name='institution_ward')
    coord = models.GeometryField()
    last_verified_year = models.ForeignKey('AcademicYear')
    status = models.ForeignKey('Status')
