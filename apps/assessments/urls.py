from django.conf.urls import url

from assessments.api_views import QGroupAnswerAPIView


urlpatterns = [
    url(r'survey/(?P<survey_id>[0-9]+)/qgroup_institution/answers',
        QGroupAnswerAPIView.as_view(), name='answergroup_institution'),
]
