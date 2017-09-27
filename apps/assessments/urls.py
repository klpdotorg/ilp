from django.conf.urls import url

from assessments.api_views import StoryMetaView


urlpatterns = [
    url(r'stories/meta/', StoryMetaView.as_view())   
]
