from django.conf.urls import url

from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter

from schools.api_view import (
    InstitutionBasicViewSet, InstitutionInfoViewSet
)
from schools.api_view import (
    StudentViewSet, StudentGroupViewSet, StudentStudentGroupViewSet
)

nested_router = ExtendedSimpleRouter()
router = DefaultRouter()

router.register(r'schools/list', InstitutionBasicViewSet, base_name='basic')
router.register(r'schools/info', InstitutionInfoViewSet, base_name='info')

## Institution -> StudentGroup -> Students
nested_router.register(
    r'institutions',
    InstitutionBasicViewSet,
    base_name='institution'
    ).register(
        r'studentgroups',
        StudentGroupViewSet,
        base_name='studentgroup',
        parents_query_lookups=['institution']
        ).register(
            r'students',
            StudentViewSet,
            base_name='students',
            parents_query_lookups=['studentgroups__institution',
            'institution']
        )

urlpatterns = router.urls + nested_router.urls
