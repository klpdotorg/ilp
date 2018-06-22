from rest_framework.routers import DefaultRouter

from rest_framework_extensions.routers import ExtendedSimpleRouter

from django.conf.urls import url

from schools.api_view import (
    InstitutionViewSet, InstitutionCategoryListView,
    InstitutionManagementListView, InstitutionDemographics,
    InstitutionInfra, InstitutionFinance, InstitutionSummaryView,
    MergeEndpoints, OmniSearch, InstitutionLanguageListView
)
from schools.api_view import (
    StudentViewSet, StudentGroupViewSet, StudentStudentGroupViewSet,
    ProgrammeViewSet, StaffViewSet, InstituteStudentsViewSet, InstituteStudentGroupViewSet
)
from schools.views import SchoolPageView

nested_router = ExtendedSimpleRouter()
router = DefaultRouter()

router.register(r'teachers', StaffViewSet, base_name='teacher')
router.register(r'institutestudents', InstituteStudentsViewSet, base_name='institutestudent')
router.register(r'institutestudentgroups', InstituteStudentGroupViewSet, base_name='institutestudentgroup')

# Institution -> StudentGroup -> Students
institution_routes = nested_router.register(
    r'institutions',
    InstitutionViewSet,
    base_name='institution'
)
institution_routes.register(
    r'studentgroups',
    StudentGroupViewSet,
    base_name='institutions-studentgroup',
    parents_query_lookups=['institution']
)
institution_routes.register(
    r'students',
    StudentViewSet,
    base_name='institutions-student',
    parents_query_lookups=['institution']
)

# StudentGroups -> Students -> StudentStudentGroupRelation
nested_router.register(
    r'studentgroups',
    StudentGroupViewSet,
    base_name='studentgroup',
    ).register(
        r'students',
        StudentViewSet,
        base_name='studentgroups-student',
        parents_query_lookups=['studentgroups']
        ).register(
            r'enrollment',
            StudentStudentGroupViewSet,
            base_name='studentstudentgrouprelation',
            parents_query_lookups=['student__studentgroups', 'student']
        )

# Programme
nested_router.register(r'programmes', ProgrammeViewSet, base_name='programme')

urlpatterns = [
    url(r'^merge$', MergeEndpoints.as_view(), name='api_merge'),
    url(r'^search/$', OmniSearch.as_view(), name='api_omni_search'),
    url(r'^institution/categories$',
        InstitutionCategoryListView.as_view(),
        name='inst-category'),
    url(r'^institution/managements$',
        InstitutionManagementListView.as_view(),
        name='inst-management'),
    url(r'^institutions/list$',
        InstitutionSummaryView.as_view(),
        name='inst-list'),
    url(r'^institution/(?P<pk>[0-9]+)/languages/$',
        InstitutionLanguageListView.as_view(),
        name='inst-language'),
    url(r'^institutions/(?P<pk>[0-9]+)/demographics$',
        InstitutionDemographics.as_view(),
        name='inst-demographics'),
    url(r'^institutions/(?P<pk>[0-9]+)/infrastructure$',
        InstitutionInfra.as_view(),
        name='inst-infra'),
    url(r'^institutions/(?P<pk>[0-9]+)/finance$',
        InstitutionFinance.as_view(),
        name='inst-finance'),
] + router.urls + nested_router.urls
