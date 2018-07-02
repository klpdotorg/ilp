from django.conf.urls import url
from rest_framework import routers
from permissions.api_views import PermissionView

urlpatterns = [
    url(
        r'^users/(?P<pk>[0-9]+)/permissions/$',
        PermissionView.as_view(),
        name='permissions_view'
    ),
    
]