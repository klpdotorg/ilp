from common.serializers import KLPSerializer, KLPSimpleGeoSerializer
from rest_framework import serializers
from boundary.models import Boundary

class BoundarySerializer(KLPSerializer):
    class Meta:
        model = Boundary
        fields = ('id', 'name', 'dise_slug', 'boundary_type', 'type', 'status')
