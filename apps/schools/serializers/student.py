from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin
)

from schools.models import (
    Student, StudentGroup, StudentStudentGroupRelation
)


class StudentSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    # relations = RelationsSerializer(many='True')

    class Meta:
        model = Student
        fields = (
            'id', 'first_name', 'middle_name', 'last_name', 'uid', 'dob',
            'gender', 'mt', 'status',
            # 'relations'
        )
        list_serializer_class = BulkListSerializer

    def create(self, validated_data):
        studentgroup_id = self.context['view'].\
            kwargs['parent_lookup_studentgroups']
        active = validated_data.get('active', 2)
        try:
            student_group = StudentGroup.objects.get(id=studentgroup_id)
        except:
            raise ValidationError(studentgroup_id + " not found.")

        # relations_data = validated_data.pop('relations')
        student = Student.objects.create(**validated_data)
        # for item in relations_data:
        #     relation = Relations.objects.create(student=student,**item)
        student.save()

        StudentStudentGroupRelation.objects.get_or_create(
            student=student, student_group=student_group,
            active=active,
        )

        return student

    def update(self, instance, validated_data):
        relations_data = validated_data.pop('relations')
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.middle_name = validated_data.get(
            'middle_name', instance.middle_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.uid = validated_data.get('uid', instance.uid)
        instance.save()
        # relations = Relations.objects.filter(student_id=instance.id)
        for item in relations_data:
            # relation = Relations.objects.get(id=item['id'])
            # If firstname, lastname and middle name are empty,
            # delete the relation
            # relation.relation_type = item.get('relation_type')
            # If all the names are empty, delete the relation
            # first_name = item.get('first_name')
            # middle_name = item.get('middle_name')
            # last_name = item.get('last_name')
            # if not first_name and not middle_name and not last_name:
            #     relation.delete()
            # else:
            #     relation.first_name = item.get('first_name')
            #     relation.middle_name = item.get('middle_name')
            #     relation.last_name = item.get('last_name')
            #     relation.save()
            pass
        instance.save()
        return instance

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
