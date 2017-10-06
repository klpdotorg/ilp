from django.conf.urls import url
from assessments.api_views import(
         StoryMetaView, SurveysViewSet,
         QuestionGroupViewSet, QuestionViewSet, QuestionGroupQuestions,
         QuestionGroupAnswers)
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

nested_router = ExtendedSimpleRouter()
simple_router = routers.DefaultRouter()

simple_router.register(r'surveys/questions',       QuestionViewSet, base_name='survey-questions')

# surveys -> questiongroup -> questions maps to earlier programs -> # assessments -> questions

nested_router.register(
    r'surveys',
    SurveysViewSet,
    base_name='surveys').register(
        r'questiongroup',
        QuestionGroupViewSet,
        base_name="surveys-questiongroup",
        parents_query_lookups=['survey']).register(
            r'questions', QuestionGroupQuestions,
            base_name="surveys-questiongroup-questions",
            parents_query_lookups=['survey', 'questiongroup_id']
        )

# surveys -> questiongroup -> answers maps to earlier programs ->
# assessments -> answers
nested_router.register(
    r'surveys',
    SurveysViewSet,
    base_name='surveys').register(
        r'questiongroup',
        QuestionGroupViewSet,
        base_name="surveys-questiongroup",
        parents_query_lookups=['survey']).register(
            r'answers', QuestionGroupAnswers,
            base_name="surveys-questiongroup-answers",
            parents_query_lookups=['survey', 'questiongroup_id']
        )

urlpatterns = [
    url(r'stories/meta/', StoryMetaView.as_view(),
        name='storymetaview'), ] + simple_router.urls + nested_router.urls
