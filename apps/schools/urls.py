from django.conf.urls import url

from rest_framework_extensions.routers import ExtendedSimpleRouter

from schools.api_view import (
    InstitutionListView, InstitutionInfoView
)
from schools.api_view import (
    StudentViewSet, StudentGroupViewSet, StudentStudentGroupViewSet
)


school_apis = [
    url(r'^schools/list/$',
        InstitutionListView.as_view(), name='institution-list'),
    url(r'^schools/info/$',
        InstitutionInfoView.as_view(), name='institution-info'),
]

student_apis = ExtendedSimpleRouter()
student_apis.register(
    r'students',
    StudentViewSet,
    base_name='students',
    ).register(
        r'studentgroups',
        StudentGroupViewSet,
        base_name='nested_students',
        parents_query_lookups=['students']
        ).register(
            r'enrollment',
            StudentStudentGroupViewSet,
            base_name='studentstudentgrouprelation',
            parents_query_lookups=['student_id', 'student_group']
        )

urlpatterns = school_apis + student_apis.urls
