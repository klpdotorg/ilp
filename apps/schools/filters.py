import django_filters
from schools.models import Student, StudentGroup


class StudentFilter(django_filters.FilterSet):

    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'status']


class StudentGroupFilter(django_filters.FilterSet):

    class Meta:
        model = StudentGroup
        fields = ['name', 'section', 'status', 'group_type']
