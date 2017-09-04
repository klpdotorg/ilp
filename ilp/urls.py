from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
            url(r'^admin/', admin.site.urls),

                # API URLs.
                    url(r'^api/v1/', include('ilp.api_urls')),
                    ]

