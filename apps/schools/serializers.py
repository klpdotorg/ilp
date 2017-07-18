from rest_framework import serializers
from schools.models import Institution

from boundary.serializers import BoundarySerializer


class InstitutionListSerializer(serializers.ModelSerializer):
    boundary = BoundarySerializer(source='admin3')
    admin1 = serializers.CharField(source='admin1.name')
    admin2 = serializers.CharField(source='admin2.name')
    admin3 = serializers.CharField(source='admin3.name')

    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address', 'boundary', 'admin1', 'admin2',
            'admin3',
        )
