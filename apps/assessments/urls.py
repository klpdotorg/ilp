from django.conf.urls import url
from assessments.api_views import (
    SurveysViewSet, QuestionGroupViewSet,
    QuestionViewSet, QuestionGroupQuestions,
    QGroupStoriesInfoView, SurveySummaryAPIView,
    SurveyInfoSourceAPIView, SurveyInfoBoundarySourceAPIView,
    SurveyInfoUserAPIView, SurveyInfoRespondentAPIView,
    SurveyInfoSchoolAPIView, SurveyInfoBoundaryAPIView,
    AnswerGroupInstitutionViewSet, AnswersInstitutionViewSet,
    SurveyDetailSourceAPIView, SurveyDetailKeyAPIView,
    SurveyInfoClassGenderAPIView, SurveyInfoEBoundaryAPIView,
    SurveyDetailClassAPIView, AnswerGroupStudentsViewSet,
    AnswersStudentViewSet, SharedAssessmentsView, SurveyVolumeAPIView,
    SurveyClassQuestionKeyAPIView, SurveyQuestionGroupQuestionKeyAPIView,
    QuestionGroupSchoolViewSet, SurveyQuestionGroupDetailsAPIView,
    SurveyInstitutionAnsAggView, SurveyInstitutionDetailAPIView,
    SurveyTagAggAPIView, AssessmentsImagesView, AssessmentSyncView,
    RespondentTypeList, ShareYourStoryAPIView,
    QuestionGroupInstitutionAssociationViewSet,
    QuestionGroupStudentGroupAssociationViewSet,
    SurveyUserSummary, SurveyBoundaryNeighbourInfoAPIView,
    SurveyBoundaryNeighbourDetailAPIView, SurveyDetailEBoundaryAPIView,
    SurveyUsersCountAPIView, SurveyBoundaryAPIView, SurveyInstitutionAPIView
)
from schools.api_view import InstitutionViewSet, StudentViewSet
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter

nested_router = ExtendedSimpleRouter()
simple_router = routers.DefaultRouter()

simple_router.register(
    r'surveys/questions', QuestionViewSet, base_name='survey-questions')
simple_router.register(
    r'survey/questiongroup/school',
    QuestionGroupSchoolViewSet, base_name='questiongroup-school',
)

# Endpoint to map assessments to institutions
nested_router.register(
    r'questiongroupinstitutionmap',
    QuestionGroupInstitutionAssociationViewSet,
    base_name='questiongroupinstitutionmap')
nested_router.register(
    r'questiongroupstudentgroupmap',
    QuestionGroupStudentGroupAssociationViewSet,
    base_name='questiongroupstudentgroupmap')

# surveys -> questiongroup -> questions
# maps to earlier programs -> # assessments -> questions
nested_router\
    .register(
        r'surveys',
        SurveysViewSet,
        base_name='surveys')\
    .register(
        r'questiongroup',
        QuestionGroupViewSet,
        base_name="surveys-questiongroup",
        parents_query_lookups=['survey'])\
    .register(
        r'questions', QuestionGroupQuestions,
        base_name="surveys-questiongroup-questions",
        parents_query_lookups=[
            'survey', 'questiongroup']
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

# Add-on to above base route.
# surveys -> questiongroup -> institution -> answergroup -> answers
answergroup = surveyqgroup.\
    register(
        r'answergroup', AnswerGroupInstitutionViewSet,
        base_name="survey-qgroup-answergroup",
        parents_query_lookups=['survey', 'questiongroup', 'institution']
    ).\
    register(
        r'answers',
        AnswersInstitutionViewSet,
        base_name="survey-qgroup-ansgroup-answers",
        parents_query_lookups=[
            'survey', 'questiongroup', 'institution', 'answergroup']
    )

# surveys -> questiongroup -> institution -> answers
answers = surveyqgroup.register(
        r'answers',
        AnswersInstitutionViewSet,
        base_name="qgroup-institution-answers",
        parents_query_lookups=['survey', 'questiongroup', 'institution']
    )

# surveys -> questiongroup -> students base route
surveyqgroup = nested_router.register(
    r'surveys',
    SurveysViewSet,
    base_name='survey').register(
        r'questiongroup',
        QuestionGroupViewSet,
        base_name="survey-qgroup",
        parents_query_lookups=['survey']).register(
            r'student', StudentViewSet,
            base_name='survey-qgroup-students',
            parents_query_lookups=['questiongroup', 'questiongroup__survey'])

# Add-on to above base route.
# surveys -> questiongroup -> students -> answergroup -> answers
answergroup = surveyqgroup.register(
        r'answergroup', AnswerGroupStudentsViewSet,
        base_name="survey-qgroup-answergroup",
        parents_query_lookups=['survey', 'questiongroup', 'student']
    ).register(
        r'answers', AnswersStudentViewSet,
        base_name="survey-qgroup-ansgroup-answers",
        parents_query_lookups=[
            'survey', 'questiongroup', 'student', 'answergroup']
    )

# surveys-> questiongroup -> students-> answers
answers = surveyqgroup.register(
    r'answers', AnswersStudentViewSet,
    base_name="qgroup-student-answers",
    parents_query_lookups=['survey', 'questiongroup', 'student']
)


urlpatterns = [
    url(r'sys/(?P<schoolid>[0-9]+)/$',
        ShareYourStoryAPIView.as_view({'post': 'create'}),
        name='sys_post'),
    url(r'institutionsurveys/$',
        SurveyInstitutionAnsAggView.as_view(),
        name='stories'),
    url(r'surveys/storiesinfo/$',
        QGroupStoriesInfoView.as_view(),
        name='stories-info'),
    url(r'survey/institution/detail/$',
        SurveyInstitutionDetailAPIView.as_view(),
        name='survey-institution-detial'),
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
    url(r'survey/info/boundary/source/$',
        SurveyInfoBoundarySourceAPIView.as_view(),
        name='survey-info-boundary-source'),
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
    url(r'survey/detail/class/key/$',
        SurveyClassQuestionKeyAPIView.as_view(),
        name='survey-detail-class-key'),
    url(r'survey/detail/questiongroup/key/$',
        SurveyQuestionGroupQuestionKeyAPIView.as_view(),
        name='survey-detail-class-key'),
    url(r'survey/volume/$',
        SurveyVolumeAPIView.as_view(),
        name='survey-volume'),
    url(r'survey/detail/class/$',
        SurveyDetailClassAPIView.as_view(),
        name='survey-detail-class'),
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
] + simple_router.urls + nested_router.urls
