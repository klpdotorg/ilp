from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('boundary.urls', namespace='boundary')),
    url(r'^', include('schools.urls', namespace='institution')),
    url(r'^', include('assessments.urls', namespace='surveys')),
    url(r'^', include('users.urls', namespace='user')),
]
