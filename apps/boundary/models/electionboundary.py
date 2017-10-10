from django.contrib.gis.db import models


class ElectionBoundary(models.Model):
    """ Election boundaries """
    state = models.ForeignKey('Boundary')
    dise_slug = models.CharField(max_length=300, blank=True)
    elec_comm_code = models.IntegerField(null=True)
    const_ward_name = models.CharField(max_length=300, null=True)
    const_ward_type = models.ForeignKey('BoundaryType')
    current_elected_rep = models.CharField(max_length=300, null=True)
    current_elected_party = models.ForeignKey('ElectionParty', null=True)
    status = models.ForeignKey('common.Status')
    geom = models.GeometryField(null=True)

    class Meta:
        ordering = ['const_ward_name', ]

    def __unicode__(self):
        return '%s' % self.name


class ElectionNeighbours(models.Model):
    """Neighbouring election boundaries"""
    elect_boundary = models.ForeignKey('ElectionBoundary')
    neighbour = models.ForeignKey(
        'ElectionBoundary', related_name='electionboundary_neighbour')

    class Meta:
        unique_together = (('elect_boundary', 'neighbour'), )


class ElectionParty(models.Model):
    """Election Party"""
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )


class ElectionBoundaryAggregation(models.Model):
    """Data aggregation per Elected Rep"""
    eid = models.ForeignKey('ElectionBoundary')
    name = models.CharField(max_length=300)
    academic_year = models.ForeignKey('common.AcademicYear')
    gender = models.ForeignKey('common.Gender')
    moi = models.ForeignKey('common.Language', related_name='e_agg_moi')
    mt = models.ForeignKey('common.Language', related_name='e_agg_mt')
    religion = models.ForeignKey('common.Religion')
    category = models.ForeignKey('common.StudentCategory')
    num = models.IntegerField()

    class Meta:
        unique_together = (
            ('id', 'academic_year', 'gender', 'moi', 'mt',
             'religion', 'category'),
        )
