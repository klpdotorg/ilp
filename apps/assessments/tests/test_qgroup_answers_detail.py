from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase


class QGroupAnsDetailTestAPI(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'answergroup_institution.json'))
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'answer_institution.json'))
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'qgroup_questions.json'))

    def test_survey_answers_meta(self):
        url = reverse('surveys:qgroup-answers-detail',
                      kwargs={'survey_id': 7, 'qgroup_id': 20})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
