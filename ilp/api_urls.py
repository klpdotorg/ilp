from django.conf.urls import url, include

urlpatterns = [
    url(r'^(?P<state>[a-zA-z]{2})/', include('boundary.urls')),
    url(r'^(?P<state>[a-zA-z]{2})/', include('schools.urls'))
]
