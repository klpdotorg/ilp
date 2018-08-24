from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework import status

from schools.models import (
    Student, StudentGroup, StudentStudentGroupRelation
)
from common.models import Status, AcademicYear


class StudentGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudentGroup
        fields = (
            'id', 'institution', 'name', 'section', 'status', 'group_type'
        )


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = (
            'id', 'first_name', 'middle_name', 'last_name',
            'uid', 'dob', 'gender', 'mt', 'status',
            'institution', 'father_name', 'mother_name'
        )

    def validate_uid(self, uid):
        if not uid:
            return uid
        if Student.objects.filter(uid=uid).exists():
            raise serializers.ValidationError(uid + " uid already exists.")
        if not len(str(uid)) == 9:
            raise serializers.ValidationError("uid should be of 9 digits.")
        return uid

    def create(self, validated_data):
        studentgroup_id = self.context['view'].kwargs[
            'parent_lookup_studentgroups']
        try:
            student_group = StudentGroup.objects.get(id=studentgroup_id)
        except:
            raise NotFound(studentgroup_id + " not found.")

        academic_year = AcademicYear.objects.get(
            char_id=settings.DEFAULT_ACADEMIC_YEAR)
        student_status = validated_data.get('status', Status.ACTIVE)
        student = Student.objects.create(**validated_data)
        student.save()
        StudentStudentGroupRelation.objects.get_or_create(
            student=student, student_group=student_group,
            status=student_status, academic_year=academic_year
        )
        return student


class StudentSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id', 'first_name', 'middle_name', 'last_name',
            'uid', 'dob', 'gender', 'mt', 'status',
            'institution', 'classes', 'father_name',
            'mother_name'
        )

    def get_classes(self, student):
        groups = StudentStudentGroupRelation.objects.filter(
            student=student, status='AC')
        studentgroup_id = groups.values_list('student_group', flat=True)
        qs = StudentGroup.objects.filter(
            id__in=studentgroup_id, group_type='class')
        return StudentGroupSerializer(qs, many=True).data


class StudentStudentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentStudentGroupRelation
        fields = (
            'id', 'student', 'student_group', 'academic_year', 'status'
        )
