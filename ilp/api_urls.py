from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('boundary.urls', namespace='boundary')),
    url(r'^', include('schools.urls', namespace='institution')),
    url(r'^', include('assessments.urls', namespace='surveys')),
    url(r'^', include('common.urls', namespace='common')),
    url(r'^', include('users.urls', namespace='user')),
    url(r'^', include('ivrs.api_urls', namespace='ivrs')),
    # url(r'^', include('permissions.urls', namespace='permissions'))
]
