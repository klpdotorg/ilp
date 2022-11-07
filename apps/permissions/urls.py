from django.urls import re_path
from rest_framework import routers
from permissions.api_views import PermissionView

urlpatterns = [
    re_path(
        r'^users/(?P<pk>[0-9]+)/permissions/$',
        PermissionView.as_view(),
        name='permissions_view'
    ),
    
]

app_name = "permissions"