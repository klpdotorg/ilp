from django.contrib.gis.db import models
from common.models import common


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


class Boundary(models.Model):
    """ educational boundaries """
    parent = models.ForeignKey('self', null=True)
    name = models.CharField(max_length=300)
    boundary_type = models.ForeignKey('BoundaryType')
    type = models.ForeignKey('common.InstitutionType', null=True)
    dise_slug = models.CharField(max_length=300, blank=True)
    geom = models.GeometryField(null=True)
    status = models.ForeignKey('common.Status')
    objects = common.StatusManager()

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
        unique_together = (('boundary','neighbour'), )


class BoundaryAggregation(models.Model):
    """Data aggregation per boundary"""
    bid = models.ForeignKey('Boundary')
    name = models.CharField(max_length=300)
    academic_year = models.ForeignKey('common.AcademicYear')
    gender = models.ForeignKey('common.Gender')
    mt = models.ForeignKey('common.Language', related_name='b_agg_mt')
    religion = models.ForeignKey('common.Religion')
    category = models.ForeignKey('common.StudentCategory')
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mvw_boundary_aggregation'


class BoundaryHierarchy(models.Model):
    """boundary hierarchy details"""
    admin3_id = models.OneToOneField('Boundary', related_name='admin3_id', primary_key=True)
    admin3_name = models.CharField(max_length=300)
    admin2_id = models.ForeignKey('Boundary', related_name='admin2_id')
    admin2_name = models.CharField(max_length=300)
    admin1_id = models.ForeignKey('Boundary', related_name='admin1_id')
    admin1_name = models.CharField(max_length=300)
    admin0_id = models.ForeignKey('Boundary', related_name='admin0_id')
    admin0_name = models.CharField(max_length=300)
    type_id = models.ForeignKey('common.InstitutionType')

    class Meta:
        managed = False
        db_table = 'mvw_boundary_hierarchy'
