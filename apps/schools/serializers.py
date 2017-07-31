from rest_framework import serializers
from schools.models import Institution

from common.serializers import ILPSerializer, InstitutionTypeSerializer
from boundary.serializers import (
    BoundarySerializer, ElectionBoundarySerializer
)


class InstitutionListSerializer(ILPSerializer):
    boundary = BoundarySerializer(source='admin3')
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')
    type = InstitutionTypeSerializer(source='institution_type')

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'boundary', 'admin1', 'admin2',
            'admin3', 'type'
        )


class InstitutionInfoSerializer(ILPSerializer):
    mgmt = serializers.CharField(source='management.name')
    cat = serializers.CharField(source='category.name')
    admin1 = BoundarySerializer('admin1')
    admin2 = BoundarySerializer('admin2')
    admin3 = BoundarySerializer('admin3')
    parliament = serializers.SerializerMethodField()
    assembly = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    type = InstitutionTypeSerializer(source='institution_type')

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'cat', 'mgmt', 'landmark', 'admin1',
            'admin2', 'admin3', 'parliament', 'assembly', 'ward', 'type'
        )

    def get_parliament(self, obj):
        if obj.ward is None:
            return None
        return ElectionBoundarySerializer(obj.mp).data

    def get_assembly(self, obj):
        if obj.ward is None:
            return None
        return ElectionBoundarySerializer(obj.mla).data

    def get_ward(self, obj):
        if obj.ward is None:
            return None
        return ElectionBoundarySerializer(obj.ward).data
