from rest_framework import serializers

from common.serializers import KLPSerializer
from boundary.models import Boundary, ElectionBoundary


class BoundarySerializer(KLPSerializer):
    class Meta:
        model = Boundary
        fields = (
            'id', 'name', 'parent', 'dise_slug', 'boundary_type', 'type',
            'status'
        )


class BoundaryWithParentSerializer(ILPSerializer):
    parent_boundary = BoundarySerializer(source='parent')

    class Meta:
        model = Boundary
        fields = (
            'id', 'name', 'dise_slug', 'type', 'boundary_type',
            'parent_boundary'
        )

# class AssemblySerializer(KLPSimpleGeoSerializer):
#     class Meta:
#         model = Assembly
#         fields = ('id', 'name')


# class ParliamentSerializer(KLPSimpleGeoSerializer):
#     class Meta:
#         model = Parliament
#         fields = ('id', 'name')


class ElectionBoundarySerializer(ILPSerializer):
    name = serializers.CharField(source='const_ward_name')

    class Meta:
        model = ElectionBoundary
        fields = ('id', 'name')
