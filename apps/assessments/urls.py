from django.conf.urls import url
from assessments.api_views import(
    SurveysViewSet, QuestionGroupViewSet,
    QuestionViewSet, QuestionGroupQuestions,
    QGroupStoriesInfoView, SurveySummaryAPIView,
    SurveyInfoSourceAPIView, SurveyInfoBoundarySourceAPIView,
    SurveyInfoUserAPIView, SurveyInfoRespondentAPIView,
    SurveyInfoSchoolAPIView, SurveyInfoBoundaryAPIView,
    AnswerGroupInstitutionViewSet, AnswersInstitutionViewSet,
    SurveyDetailSourceAPIView, SurveyDetailKeyAPIView,
    SurveyInfoClassGenderAPIView, SurveyInfoEBoundaryAPIView,
    SurveyDetailClassAPIView
)
from schools.api_view import InstitutionViewSet
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

nested_router = ExtendedSimpleRouter()
simple_router = routers.DefaultRouter()

simple_router.register(
    r'surveys/questions', QuestionViewSet, base_name='survey-questions')

# surveys -> questiongroup -> questions
# maps to earlier programs -> # assessments -> questions

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

# surveys -> questiongroup -> institution base route
surveyqgroup = nested_router.register(
    r'surveys',
    SurveysViewSet,
    base_name='survey').register(
        r'qgroup',
        QuestionGroupViewSet,
        base_name="survey-qgroup",
        parents_query_lookups=['survey']).register(
            r'institution', InstitutionViewSet,
            base_name='survey-qgroup-institution',
            parents_query_lookups=['qgroup', 'qgroup__survey'])
 
# Add-on to above base route. surveys -> questiongroup -> institution -> answergroup -> answers
answergroup =  surveyqgroup.register(
            r'answergroup', AnswerGroupInstitutionViewSet,
            base_name="survey-qgroup-answergroup",
            parents_query_lookups=['survey','questiongroup','institution']
       ).register(r'answers',AnswersInstitutionViewSet,base_name="survey-qgroup-ansgroup-answers",
            parents_query_lookups=['survey', 'questiongroup', 'institution', 'answergroup'])

# surveys->questiongroup->institution->answers
answers = surveyqgroup.register(r'answers', AnswersInstitutionViewSet,
                                base_name="qgroup-institution-answers",
                                parents_query_lookups=['survey', 'questiongroup', 'institution'])

urlpatterns = [
    url(r'surveys/storiesinfo',
        QGroupStoriesInfoView.as_view(), name='stories-info'),
    url(r'survey/summary',
        SurveySummaryAPIView.as_view(), name='survey-summary'),
    url(r'survey/info/source',
        SurveyInfoSourceAPIView.as_view(), name='survey-info-source'),
    url(r'survey/info/school',
        SurveyInfoSchoolAPIView.as_view(), name='survey-info-school'),
    url(r'survey/info/boundary',
        SurveyInfoBoundaryAPIView.as_view(), name='survey-info-boundary'),
    url(r'survey/info/boundary/source',
        SurveyInfoBoundarySourceAPIView.as_view(),
        name='survey-info-boundary-source'),
    url(r'survey/info/respondent', SurveyInfoRespondentAPIView.as_view(),
        name='survey-info-respondent'),
    url(r'survey/info/users', SurveyInfoUserAPIView.as_view(),
        name='survey-info-user'),
    url(r'survey/detail/source', SurveyDetailSourceAPIView.as_view(),
        name='survey-detail-source'),
    url(r'survey/detail/key', SurveyDetailKeyAPIView.as_view(),
        name='survey-detail-key'),
    url(r'survey/detail/class', SurveyDetailClassAPIView.as_view(),
        name='survey-detail-class'),
    url(r'survey/info/class/gender', SurveyInfoClassGenderAPIView.as_view(),
        name='survey-info-class-gender'),
    url(r'survey/info/electionboundary', SurveyInfoEBoundaryAPIView.as_view(),
        name='survey-info-class-gender'),
] + simple_router.urls + nested_router.urls
