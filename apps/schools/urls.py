from django.conf.urls import url

from rest_framework_extensions.routers import ExtendedSimpleRouter

from schools.api_view import (
    InstitutionListView, InstitutionInfoView
)
from schools.api_view import (
    StudentViewSet, StudentGroupViewSet, StudentStudentGroupViewSet
)

studentgroup_list = StudentGroupViewSet.as_view({
    'get': 'list',
})

studentgroup_detail = StudentGroupViewSet.as_view({
    'get': 'retrieve'
    # 'put': 'update',
    # 'patch': 'partial-update',
    # 'delete': 'destroy'
})

school_apis = [
    url(r'^schools/list/$',
        InstitutionListView.as_view(), name='institution-list'),
    url(r'^schools/info/$',
        InstitutionInfoView.as_view(), name='institution-info'),
    url(r'^schools/(?P<id>[0-9]+)/studentgroups$', studentgroup_list, name='studentgroup-list'),
    url(r'^schools/(?P<id>[0-9]+)/studentgroups/(?P<studentgroupid>[0-9]+)$', studentgroup_detail, name='studentgroup-detail')        
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

# studentgroup_apis = ExtendedSimpleRouter()
# studentgroup_apis.register(r'studentgroups', StudentGroupViewSet, base_name='studentgroups')

## StudentGroups -> Students -> StudentStudentGroupRelation
student_apis.register(
    r'studentgroups',
    StudentGroupViewSet,
    base_name='studentgroup',
    ).register(
        r'students',
        StudentViewSet,
        base_name='nested_students',
        parents_query_lookups=['studentgroups']
        ).register(
            r'enrollment',
            StudentStudentGroupViewSet,
            base_name='studentstudentgrouprelation',
            parents_query_lookups=['student__studentgroups', 'student']
        )

## Institution -> StudentGroup -> Students
student_apis.register(
    r'institutions',
    InstitutionViewSet,
    base_name='institution'
    ).register(
        r'studentgroups',
        StudentGroupViewSet,
        base_name='studentgroup',
        parents_query_lookups=['institution']
        ).register(
            r'students',
            StudentViewSet,
            base_name='nested_students',
            parents_query_lookups=['studentgroups__institution', 'studentgroups']
        )

urlpatterns = school_apis + student_apis.urls
