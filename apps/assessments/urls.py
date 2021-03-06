from django.conf.urls import url
from assessments.api_views import (
    SurveysViewSet, QuestionGroupViewSet,
    QuestionViewSet, QuestionGroupQuestions,
    QuestionTypeListView,
    QGroupStoriesInfoView, SurveySummaryAPIView,
    SurveyInfoSourceAPIView, SurveyInfoUserAPIView,
    SurveyInfoRespondentAPIView, SurveyInfoSchoolAPIView,
    SurveyInfoBoundaryAPIView, SurveyDetailSourceAPIView,
    SurveyDetailKeyAPIView, SurveyInfoClassGenderAPIView,
    SurveyInfoEBoundaryAPIView, 
    SharedAssessmentsView, SurveyVolumeAPIView,
    SurveyQuestionGroupQuestionKeyAPIView,
    SurveyQuestionGroupDetailsAPIView, SurveyInstitutionAnsAggView,
    SurveyTagAggAPIView, AnswerGroupViewSet, AssessmentsImagesView,
    AssessmentSyncView, RespondentTypeList, ShareYourStoryAPIView,
    SurveyUserSummary, SurveyBoundaryNeighbourInfoAPIView,
    AnswerViewSet, SurveyBoundaryNeighbourDetailAPIView,
    SurveyDetailEBoundaryAPIView, SurveyUsersCountAPIView,
    SurveyBoundaryAPIView, SurveyInstitutionAPIView,
    BoundaryQuestionGroupMapping, SurveyAssociateBoundaryAPIView,
    SurveyAssociateInstitutionAPIView, SurveyPartnersViewSet,
    SurveySourceViewSet, SurveyTypeListView,
    SurveyQuestionGroupQDetailsAPIView, SurveyInstitutionLocationAPIView,
    SurveyGPAPIView, SurveyQuestionGroupQuestionKeyYearComparisonAPIView
)
from schools.api_view import (
    InstitutionViewSet, StudentViewSet, StudentGroupViewSet
)
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

nested_router = ExtendedSimpleRouter()
simple_router = routers.DefaultRouter()

simple_router.register(
    r'surveys/questions',
    QuestionViewSet,
    basename='survey-questions'
)
#survey/partner URL
simple_router.register(
    r'surveys/partners',
    SurveyPartnersViewSet,
    basename='survey-partners'
)

simple_router.register(
    r'surveys/sources',
    SurveySourceViewSet,
    basename='survey-sources'
)

# surveys -> questiongroup -> questions
# maps to earlier programs -> # assessments -> questions
questiongroup_router = \
    nested_router.register(
        r'surveys',
        SurveysViewSet,
        basename='survey').register(
            r'questiongroup',
            QuestionGroupViewSet,
            basename='survey-questiongroup',
            parents_query_lookups=['survey']
        )

questiongroup_router.register(
    r'questions', QuestionGroupQuestions,
    basename="survey-questiongroup-question",
    parents_query_lookups=[
        'survey', 'questiongroup']
)

questiongroup_router.register(
    r'answergroups', AnswerGroupViewSet,
    basename='survey-questiongroup-answergroups',
    parents_query_lookups=[
        'survey_id', 'questiongroup_id'
    ]).register(
        r'answers', AnswerViewSet,
        basename='survey-questiongroup-answergroup-answers',
        parents_query_lookups=[
            'survey_id', 'questiongroup_id', 'answergroup_id'
        ])

urlpatterns = [
    url(r'sys/(?P<schoolid>[0-9]+)/$',
        ShareYourStoryAPIView.as_view({'post': 'create'}),
        name='sys_post'),
    url(r'survey/(?P<survey_id>[0-9]+)/boundary-associations/',
        SurveyAssociateBoundaryAPIView.as_view(),
        name='survey-associate-boundaries'),
    url(r'survey/(?P<survey_id>[0-9]+)/institution-associations/',
        SurveyAssociateInstitutionAPIView.as_view(),
        name='survey-associate-institutions'),
    url(r'institutionsurveys/$',
        SurveyInstitutionAnsAggView.as_view(),
        name='stories'),
    url(r'institutionsurvey/location/$',
        SurveyInstitutionLocationAPIView.as_view(),
        name='survey_location'),
    url(r'survey/gp/$',
        SurveyGPAPIView.as_view(),
        name='survey_gp'),
    url(r'surveys/storiesinfo/$',
        QGroupStoriesInfoView.as_view(),
        name='stories-info'),
    url(r'survey/summary/$',
        SurveySummaryAPIView.as_view(),
        name='survey-summary'),
    url(r'survey/info/source/$',
        SurveyInfoSourceAPIView.as_view(),
        name='survey-info-source'),
    url(r'survey/info/school/$',
        SurveyInfoSchoolAPIView.as_view(),
        name='survey-info-school'),
    url(r'survey/info/boundary/$',
        SurveyInfoBoundaryAPIView.as_view(),
        name='survey-info-boundary'),
    url(r'survey/info/respondent/$',
        SurveyInfoRespondentAPIView.as_view(),
        name='survey-info-respondent'),
    url(r'survey/info/users/$',
        SurveyInfoUserAPIView.as_view(),
        name='survey-info-user'),
    url(r'survey/detail/source/$',
        SurveyDetailSourceAPIView.as_view(),
        name='survey-detail-source'),
    url(r'survey/detail/key/$',
        SurveyDetailKeyAPIView.as_view(),
        name='survey-detail-key'),
    url(r'survey/detail/questiongroup/key/$',
        SurveyQuestionGroupQuestionKeyAPIView.as_view(),
        name='survey-detail-class-key'),
    url(r'survey/detail/questiongroup/qdetails/$',
        SurveyQuestionGroupQDetailsAPIView.as_view(),
        name='survey-detail-questiongroup-qdetails'),
    url(r'survey/volume/$',
        SurveyVolumeAPIView.as_view(),
        name='survey-volume'),
    url(r'survey/info/class/gender/$',
        SurveyInfoClassGenderAPIView.as_view(),
        name='survey-info-class-gender'),
    url(r'survey/info/electionboundary/$',
        SurveyInfoEBoundaryAPIView.as_view(),
        name='survey-info-electionboundary'),
    url(r'survey/detail/electionboundary/$',
        SurveyDetailEBoundaryAPIView.as_view(),
        name='survey-detail-electionboundary'),
    url(r'surveys/boundary/$',
        SurveyBoundaryAPIView.as_view(),
        name='survey-boundary'),
    url(r'surveys/institution/$',
        SurveyInstitutionAPIView.as_view(),
        name='survey-institution'),
    url(r'surveys/shared-assessments/$',
        SharedAssessmentsView.as_view(),
        name='survey-shared-assessments'),
    url(r'surveys/questiongroupdetails/$',
        SurveyQuestionGroupDetailsAPIView.as_view(),
        name='survey-questiongroup-details'),
    url(r'surveys/tagmappingsummary/$',
        SurveyTagAggAPIView.as_view(),
        name='survey-tagmap-summary'),
    url(r'surveys/assessments/sync.$',
        AssessmentSyncView.as_view(),
        name='survey-assessments-sync'),
    url(r'surveys/assessments/images.$',
        AssessmentsImagesView.as_view(),
        name='survey-assessments-images'),
    url(r'surveys/assessments/respondent-types.$',
        RespondentTypeList.as_view(),
        name='survey-assessments-respondent-types'),
    url(r'surveys/usersummary/$',
        SurveyUserSummary.as_view(),
        name='survey-user-summary'),
    url(r'surveys/usercount/$',
        SurveyUsersCountAPIView.as_view(),
        name='survey-user-count'),
    url(r'surveys/boundaryneighbour/info/$',
        SurveyBoundaryNeighbourInfoAPIView.as_view(),
        name='survey-boundaryneighbour-info'),
    url(r'surveys/boundaryneighbour/detail/$',
        SurveyBoundaryNeighbourDetailAPIView.as_view(),
        name='survey-boundaryneighbour-detail'),
    url(r'^boundary/questiongroup-map/$',
        BoundaryQuestionGroupMapping.as_view(),
        name='boundary-qgroup-map'),
    url(r'^surveys/questiontype/$',
        QuestionTypeListView.as_view(),
        name='question-type'),
    url(r'survey-type/',
        SurveyTypeListView.as_view(),
        name='survey-type'),
    url(r'survey/comparison/year',
        SurveyQuestionGroupQuestionKeyYearComparisonAPIView.as_view(),
        name='survey_comparision_year')
] + simple_router.urls + nested_router.urls

app_name = "assessments"