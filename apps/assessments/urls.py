from django.urls import re_path
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
    re_path(r'sys/(?P<schoolid>[0-9]+)/$',
        ShareYourStoryAPIView.as_view({'post': 'create'}),
        name='sys_post'),
    re_path(r'survey/(?P<survey_id>[0-9]+)/boundary-associations/',
        SurveyAssociateBoundaryAPIView.as_view(),
        name='survey-associate-boundaries'),
    re_path(r'survey/(?P<survey_id>[0-9]+)/institution-associations/',
        SurveyAssociateInstitutionAPIView.as_view(),
        name='survey-associate-institutions'),
    re_path(r'institutionsurveys/$',
        SurveyInstitutionAnsAggView.as_view(),
        name='stories'),
    re_path(r'institutionsurvey/location/$',
        SurveyInstitutionLocationAPIView.as_view(),
        name='survey_location'),
    re_path(r'survey/gp/$',
        SurveyGPAPIView.as_view(),
        name='survey_gp'),
    re_path(r'surveys/storiesinfo/$',
        QGroupStoriesInfoView.as_view(),
        name='stories-info'),
    re_path(r'survey/summary/$',
        SurveySummaryAPIView.as_view(),
        name='survey-summary'),
    re_path(r'survey/info/source/$',
        SurveyInfoSourceAPIView.as_view(),
        name='survey-info-source'),
    re_path(r'survey/info/school/$',
        SurveyInfoSchoolAPIView.as_view(),
        name='survey-info-school'),
    re_path(r'survey/info/boundary/$',
        SurveyInfoBoundaryAPIView.as_view(),
        name='survey-info-boundary'),
    re_path(r'survey/info/respondent/$',
        SurveyInfoRespondentAPIView.as_view(),
        name='survey-info-respondent'),
    re_path(r'survey/info/users/$',
        SurveyInfoUserAPIView.as_view(),
        name='survey-info-user'),
    re_path(r'survey/detail/source/$',
        SurveyDetailSourceAPIView.as_view(),
        name='survey-detail-source'),
    re_path(r'survey/detail/key/$',
        SurveyDetailKeyAPIView.as_view(),
        name='survey-detail-key'),
    re_path(r'survey/detail/questiongroup/key/$',
        SurveyQuestionGroupQuestionKeyAPIView.as_view(),
        name='survey-detail-class-key'),
    re_path(r'survey/detail/questiongroup/qdetails/$',
        SurveyQuestionGroupQDetailsAPIView.as_view(),
        name='survey-detail-questiongroup-qdetails'),
    re_path(r'survey/volume/$',
        SurveyVolumeAPIView.as_view(),
        name='survey-volume'),
    re_path(r'survey/info/class/gender/$',
        SurveyInfoClassGenderAPIView.as_view(),
        name='survey-info-class-gender'),
    re_path(r'survey/info/electionboundary/$',
        SurveyInfoEBoundaryAPIView.as_view(),
        name='survey-info-electionboundary'),
    re_path(r'survey/detail/electionboundary/$',
        SurveyDetailEBoundaryAPIView.as_view(),
        name='survey-detail-electionboundary'),
    re_path(r'surveys/boundary/$',
        SurveyBoundaryAPIView.as_view(),
        name='survey-boundary'),
    re_path(r'surveys/institution/$',
        SurveyInstitutionAPIView.as_view(),
        name='survey-institution'),
    re_path(r'surveys/shared-assessments/$',
        SharedAssessmentsView.as_view(),
        name='survey-shared-assessments'),
    re_path(r'surveys/questiongroupdetails/$',
        SurveyQuestionGroupDetailsAPIView.as_view(),
        name='survey-questiongroup-details'),
    re_path(r'surveys/tagmappingsummary/$',
        SurveyTagAggAPIView.as_view(),
        name='survey-tagmap-summary'),
    re_path(r'surveys/assessments/sync.$',
        AssessmentSyncView.as_view(),
        name='survey-assessments-sync'),
    re_path(r'surveys/assessments/images.$',
        AssessmentsImagesView.as_view(),
        name='survey-assessments-images'),
    re_path(r'surveys/assessments/respondent-types.$',
        RespondentTypeList.as_view(),
        name='survey-assessments-respondent-types'),
    re_path(r'surveys/usersummary/$',
        SurveyUserSummary.as_view(),
        name='survey-user-summary'),
    re_path(r'surveys/usercount/$',
        SurveyUsersCountAPIView.as_view(),
        name='survey-user-count'),
    re_path(r'surveys/boundaryneighbour/info/$',
        SurveyBoundaryNeighbourInfoAPIView.as_view(),
        name='survey-boundaryneighbour-info'),
    re_path(r'surveys/boundaryneighbour/detail/$',
        SurveyBoundaryNeighbourDetailAPIView.as_view(),
        name='survey-boundaryneighbour-detail'),
    re_path(r'^boundary/questiongroup-map/$',
        BoundaryQuestionGroupMapping.as_view(),
        name='boundary-qgroup-map'),
    re_path(r'^surveys/questiontype/$',
        QuestionTypeListView.as_view(),
        name='question-type'),
    re_path(r'survey-type/',
        SurveyTypeListView.as_view(),
        name='survey-type'),
    re_path(r'survey/comparison/year',
        SurveyQuestionGroupQuestionKeyYearComparisonAPIView.as_view(),
        name='survey_comparision_year')
] + simple_router.urls + nested_router.urls

app_name = "assessments"