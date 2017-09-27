from django.conf.urls import url
from assessments.api_views import (StoryMetaView, SurveysViewSet,
    QuestionGroupViewSet)
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

nested_router = ExtendedSimpleRouter()

nested_router.register(
    r'surveys',
    SurveysViewSet,
    base_name='surveys').register(
        r'questiongroup',
        QuestionGroupViewSet,
        base_name="surveys-questiongroup",
        parents_query_lookups=['survey'])

urlpatterns = [
    url(r'stories/meta/', StoryMetaView.as_view()),
] + nested_router.urls
