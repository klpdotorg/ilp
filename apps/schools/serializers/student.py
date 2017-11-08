from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin
)

from schools.models import (
    Student, StudentGroup, StudentStudentGroupRelation
)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'uid', 'dob',
            'gender', 'mt', 'status', "institution"
        )


class StudentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentGroup
        fields = (
            'id', 'institution', 'name', 'section', 'status', 'group_type'
        )

class StudentStudentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentStudentGroupRelation
        fields = (
            'id','student','student_group','academic_year','status'
        )
