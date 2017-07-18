from rest_framework import serializers
from schools.models import Institution


class InstitutionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = (
            'id', 'name', 'address'
        )