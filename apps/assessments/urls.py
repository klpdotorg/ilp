from django.conf.urls import url

from assessments.api_views import QGroupAnswerAPIView


urlpatterns = [
    url((
        r'survey/(?P<survey_id>[0-9]+)/qgroup/(?P<qgroup_id>[0-9]+)'
        '/answers/meta/'
        ),
        QGroupAnswerAPIView.as_view(), name='qgroup-answer-meta'),
]
