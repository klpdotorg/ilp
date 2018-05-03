from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

       
class StudentSerializer(serializers.ModelSerializer):
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), write_only=True)
    classes = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'uid',
            'dob',
            'gender',
            'mt',
            'status',
            'institution',
            'academic_year',
            'classes',
        )

        extra_kwargs = {'academic_year': {'write_only': True}}

    def create(self, validated_data):
        studentgroup_id = self.context['view'].kwargs[
            'parent_lookup_studentgroups']
        status = validated_data.get('status', Status.ACTIVE)
        try:
            student_group = StudentGroup.objects.get(id=studentgroup_id)
        except:
            raise ValidationError(studentgroup_id + " not found.")

        academic_year = validated_data.pop('academic_year')
        student = Student.objects.create(**validated_data)
        student.save()

        StudentStudentGroupRelation.objects.get_or_create(
            student=student, student_group=student_group,
            status=status, academic_year=academic_year
        )
        return student

    def get_classes(self, student):
        grps = StudentStudentGroupRelation.objects.filter(student=student, status = 'AC')
        studgrp_id = grps.values_list('student_group',flat=True)
        qs = StudentGroup.objects.filter(id__in=studgrp_id, group_type = 'class')
        return StudentGroupSerializer(qs, many=True).data

        
class StudentStudentGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentStudentGroupRelation
        fields = (
            'id', 'student', 'student_group', 'academic_year', 'status'
        )
