from schools.models import Staff
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = (
            'id','first_name', 'middle_name', 'last_name', 'institution',
            'doj', 'gender', 'mt', 'status', 'uid'
        )
