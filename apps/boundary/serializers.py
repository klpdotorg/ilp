from common.serializers import KLPSerializer, KLPSimpleGeoSerializer
from rest_framework import serializers
from boundary.models import Boundary

class BoundarySerializer(KLPSerializer):
    class Meta:
        model = Boundary
        fields = ('id', 'name', 'parent','dise_slug', 'boundary_type', 'type', 'status')

class BoundaryWithParentSerializer(KLPSerializer):
    parent_boundary = BoundarySerializer(source='parent')

    class Meta:
        model = Boundary
        fields = ('id', 'name', 'dise_slug', 'type', 'boundary_type', 'parent_boundary')

# class AssemblySerializer(KLPSimpleGeoSerializer):
#     class Meta:
#         model = Assembly
#         fields = ('id', 'name')


# class ParliamentSerializer(KLPSimpleGeoSerializer):
#     class Meta:
#         model = Parliament
#         fields = ('id', 'name')
