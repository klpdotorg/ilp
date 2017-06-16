from .choices import *
from .common import *
from django.contrib.gis.db import models


class BoundaryType(models.Model):
    """ Boundary type """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)


class Boundary(models.Model):
    """ Regional boundaries """
    id = models.IntegerField(primary_key=True)
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
    id = models.IntegerField(primary_key=True)
    state = models.ForeignKey('self')
    dise_slug = models.CharField(max_length=300)
    elec_comm_code = models.IntegerField()
    const_ward_name = models.CharField(max_length=300)
    const_ward_type = models.ForeignKey('BoundaryType')
    current_elected_rep = models.CharField(max_length=300)
    current_elected_party = models.ForeignKey('ElectionParty')
    status = models.ForeignKey('Status')


class BoundaryNeighbours(models.Model):
    id = models.IntegerField(primary_key=True)
    boundary = models.ForeignKey('Boundary')
    neighbour = models.ForeignKey(
            'Boundary', related_name='boundary_neighbour')


class ElectionNeighbours(models.Model):
    id = models.IntegerField(primary_key=True)
    elect_boundary = models.ForeignKey('ElectionBoundary')
    neighbour = models.ForeignKey(
        'ElectionBoundary', related_name='electionboundary_neighbour')


class ElectionParty(models.Model):
    char_id = models.CharField(max_length=300, primary_key=True)
    elect_boundary = models.ForeignKey('ElectionBoundary')
    neighbour = models.ForeignKey(
        'ElectionBoundary', related_name='electionparty_neighbour')

