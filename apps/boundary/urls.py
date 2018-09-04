from django.conf.urls import url
from rest_framework import routers
from .api_views import (
    Admin1sBoundary, Admin2sBoundary, Admin3sBoundary,
    Admin2sInsideAdmin1, Admin3sInsideAdmin1,
    Admin3sInsideAdmin2, AdminDetails, BoundaryViewSet,
    BoundaryTypeViewSet, AssemblyBoundariesViewSet,
    ParliamentBoundariesViewSet, BasicBoundaryAggView,
    StateList, StateListAPIView
)

assembliesListView = AssemblyBoundariesViewSet.as_view({'get': 'list'})
assemblyDetailView = AssemblyBoundariesViewSet.as_view({'get': 'retrieve'})
parliamentaryBoundariesListView = ParliamentBoundariesViewSet.as_view({'get': 'list'})
parliamentaryBoundariesDetailView = ParliamentBoundariesViewSet.as_view({'get': 'retrieve'})

router = routers.DefaultRouter()
router.register(r'boundaries', BoundaryViewSet, base_name='boundary')
router.register(r'boundarytype', BoundaryTypeViewSet, base_name='boundarytype')
urlpatterns = [
    url(r'^states/', StateListAPIView.as_view(), name='states-boundary'),
    url(r'^boundary/states$', StateList.as_view(), name='states-boundary'),
    url(r'^boundary/admin1s/', Admin1sBoundary.as_view(),
        name='admin1s-boundary'),
    url(r'^boundary/admin2s/', Admin2sBoundary.as_view(),
        name='admin2s-boundary'),
    url(r'^boundary/admin3s/', Admin3sBoundary.as_view(),
        name='admin3s-boundary'),
    url(r'^boundary/admin1/(?P<id>[0-9]+)/admin2/',
        Admin2sInsideAdmin1.as_view(),
        name="api_admin1s_admin2"),
    url(r'^boundary/admin1/(?P<id>[0-9]+)/admin3/',
        Admin3sInsideAdmin1.as_view(), name="api_admin1s_admin3"),
    url(r'^boundary/admin2/(?P<id>[0-9]+)/admin3/',
        Admin3sInsideAdmin2.as_view(), name="api_admin2s_admin3"),
    url(r'^boundary/admin/(?P<id>[0-9]+)/',
        AdminDetails.as_view(), name="api_admin_details"),
    url(r'^boundary/assemblies', assembliesListView, name="assemblyListView"),
    url(r'^boundary/parliaments', parliamentaryBoundariesListView, name='parliamentsListView'),
    url(r'^aggregation/boundary/(?P<id>[0-9]+)/schools/$',
        BasicBoundaryAggView.as_view(), name='api_aggregation_boundary_schools')
    ] +  router.urls
