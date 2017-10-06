from mock import patch

from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import (
    AnswerGroup_Institution, RespondentType
)

from assessments.tests.test_fixtures.meta import (
    INSTITUTION_ID
)


class AGroupInstitutionViewset(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'answergroup_institution.json'))

    @patch('assessments.api_views.QGroupAnswerAPIView.get_respondents',
           return_value={})
    def test_list_api(self, get_respondents):
        url = reverse('assessment:answergroup_institution',
                      kwargs={'survey_id': 6})
        response = self.client.get(url, {'state': 'ka'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
