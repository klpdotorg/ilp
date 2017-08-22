from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('boundary.urls')),
    url(r'^', include('schools.urls', namespace='institution'))
]
