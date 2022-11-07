from django.urls import re_path, include

urlpatterns = [
    re_path(r'^', include('boundary.urls', namespace='boundary')),
    re_path(r'^', include('schools.urls', namespace='institution')),
    re_path(r'^', include('assessments.urls', namespace='surveys')),
    re_path(r'^', include('common.urls', namespace='common')),
    re_path(r'^', include('users.urls', namespace='user')),
    re_path(r'^reports/', include('reports.api_urls')),
    re_path(r'^backoffice/', include('backoffice.api_urls')),
    re_path(r'^', include('ivrs.api_urls', namespace='ivrs')),
    re_path(r'^', include('permissions.urls', namespace='permissions'))
]
