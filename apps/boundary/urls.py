from django.conf.urls import url
from rest_framework import routers
from .api_views import (Admin1sBoundary, Admin2sBoundary, Admin3sBoundary,
                        Admin2sInsideAdmin1, Admin3sInsideAdmin1,
                        Admin3sInsideAdmin2, AdminDetails, BoundaryViewSet
                        )
router = routers.SimpleRouter()
router.register(r'^boundaries', BoundaryViewSet, base_name='boundary')
urlpatterns = [
    url(r'^boundary/admin1s$', Admin1sBoundary.as_view(),
        name='admin1s-boundary'),
    url(r'^boundary/admin2s$', Admin2sBoundary.as_view(),
        name='admin2s-boundary'),
    url(r'^boundary/admin3s$', Admin3sBoundary.as_view(),
        name='admin3s-boundary'),
    url(r'^boundary/admin1/(?P<id>[0-9]+)/admin2$',
        Admin2sInsideAdmin1.as_view(),
        name="api_admin1s_admin2"),
    url(r'^boundary/admin1/(?P<id>[0-9]+)/admin3$',
        Admin3sInsideAdmin1.as_view(), name="api_admin1s_admin3"),
    url(r'^boundary/admin2/(?P<id>[0-9]+)/admin3$',
        Admin3sInsideAdmin2.as_view(), name="api_admin2s_admin3"),
    url(r'^boundary/admin/(?P<id>[0-9]+)$',
        AdminDetails.as_view(), name="api_admin_details")
    ] +  router.urls
