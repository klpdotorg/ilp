import json
from django.contrib.gis.db import models
from schools.models import Institution
from django.db.models import Q

import json


class ElectionBoundary(models.Model):
    """ Election boundaries """
    state = models.ForeignKey('Boundary', on_delete=models.DO_NOTHING)
    #parent = models.ForeignKey('self', null=True, on_delete=models.DO_NOTHING)
    dise_slug = models.CharField(max_length=300, blank=True)
    elec_comm_code = models.IntegerField(null=True)
    const_ward_name = models.CharField(max_length=300, null=True)
    const_ward_lang_name = models.CharField(max_length=300, null=True)
    const_ward_type = models.ForeignKey(
        'BoundaryType', on_delete=models.DO_NOTHING)
    current_elected_rep = models.CharField(max_length=300, null=True)
    current_elected_party = models.ForeignKey(
        'ElectionParty', null=True, on_delete=models.DO_NOTHING)
    status = models.ForeignKey('common.Status', on_delete=models.DO_NOTHING)
    geom = models.GeometryField(null=True)

    def get_geometry(self):
        if hasattr(self, 'geom') and self.geom is not None:
            return json.loads(self.geom.geojson)
        else:
            return {}

    def schools(self):
        return Institution.objects.filter(
            Q(status='AC'),
            Q(mp=self) | Q(mla=self) | Q(gp=self) | Q(ward=self)
        )

    class Meta:
        ordering = ['const_ward_name', ]

    def __unicode__(self):
        return '%s' % self.name


class ElectionNeighbours(models.Model):
    """Neighbouring election boundaries"""
    elect_boundary = models.ForeignKey(
        'ElectionBoundary', on_delete=models.DO_NOTHING)
    neighbour = models.ForeignKey(
        'ElectionBoundary', 
        related_name='electionboundary_neighbour', 
        on_delete=models.DO_NOTHING)

    class Meta:
        unique_together = (('elect_boundary', 'neighbour'), )


class ElectionParty(models.Model):
    """Election Party"""
    char_id = models.CharField(max_length=300, primary_key=True)
    name = models.CharField(max_length=300)

    class Meta:
        unique_together = (('name'), )
