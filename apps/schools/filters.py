import django_filters
from schools.models import Student


class StudentFilter(django_filters.FilterSet):

    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'status']
