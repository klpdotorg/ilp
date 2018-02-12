import json

from django.contrib.gis.db import models
from common.models import common
from schools.models import Institution
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.db.models import Q


class BoundaryType(models.Model):
    '''
    Aligned to constants defined in the DB models. When those change,
    these will also have to
    change
    '''
    SCHOOL_DISTRICT = 'SD'
    SCHOOL_BLOCK = 'SB'
    SCHOOL_CLUSTER = 'SC'
    PRESCHOOL_DISTRICT = 'PD'
    PRESCHOOL_PROJECT = 'PP'
    PRESCHOOL_CIRCLE = 'PC'

    """ Boundary type """
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)
    level = models.IntegerField(null=True)

    class Meta:
        ordering = ['char_id', ]


class Boundary(models.Model):
    """ educational boundaries """
    parent = models.ForeignKey('self', null=True)
    name = models.CharField(max_length=300)
    lang_name = models.CharField(max_length=300, null=True)
    boundary_type = models.ForeignKey('BoundaryType')
    type = models.ForeignKey('common.InstitutionType', null=True)
    dise_slug = models.CharField(max_length=300, blank=True)
    geom = models.GeometryField(null=True)
    status = models.ForeignKey('common.Status')
    objects = common.StatusManager()

    def get_geometry(self):
        if hasattr(self, 'geom') and self.geom is not None:
            return json.loads(self.geom.geojson)
        else:
            return {}

    def schools(self):
        return Institution.objects.filter(
            Q(status='AC'),
            Q(admin1=self) | Q(admin2=self) | Q(admin3=self)
        )

    class Meta:
        unique_together = (('name', 'parent', 'type'), )
        ordering = ['name', ]

    def __unicode__(self):
        return '%s' % self.name


class BoundaryNeighbours(models.Model):
    """Neighbouring boundaries"""
    boundary = models.ForeignKey('Boundary')
    neighbour = models.ForeignKey(
        'Boundary', related_name='boundary_neighbour')

    class Meta:
        unique_together = (('boundary', 'neighbour'), )


class BoundaryHierarchy(models.Model):
    """boundary hierarchy details"""
    admin3_id = models.OneToOneField(
        'Boundary', related_name='admin3_id',
        db_column='admin3_id', primary_key=True)
    admin3_name = models.CharField(max_length=300)

    admin2_id = models.ForeignKey(
        'Boundary', related_name='admin2_id',
        db_column='admin2_id')
    admin2_name = models.CharField(max_length=300)

    admin1_id = models.ForeignKey(
        'Boundary', related_name='admin1_id', db_column='admin1_id')
    admin1_name = models.CharField(max_length=300)

    admin0_id = models.ForeignKey(
        'Boundary', related_name='admin0_id', db_column='admin0_id')
    admin0_name = models.CharField(max_length=300)

    type_id = models.ForeignKey('common.InstitutionType', db_column='type_id')

    class Meta:
        managed = False
        db_table = 'mvw_boundary_hierarchy'


class BoundaryStateCode(models.Model):
    """stores the state codes"""
    char_id = models.CharField(max_length=10, primary_key=True)
    boundary = models.ForeignKey('Boundary')

    class Meta:
        ordering = ['char_id', ]
