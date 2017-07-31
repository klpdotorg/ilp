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
    moi = models.ForeignKey('common.Language', related_name='b_agg_moi')
    mt = models.ForeignKey('common.Language', related_name='b_agg_mt')
    religion = models.ForeignKey('common.Religion')
    category = models.ForeignKey('common.StudentCategory')
    num = models.IntegerField()

    class Meta:
        unique_together = (('id','academic_year','gender','moi','mt','religion','category'), )
