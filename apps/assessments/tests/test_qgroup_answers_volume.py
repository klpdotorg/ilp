from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from assessments.tests.test_fixtures.meta import (
    ANSWERGROUP_INSTITUTION_IDS
)


class QGroupAnsVolTestAPI(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'answergroup_institution.json'))

    def test_survey_answers_vol_response(self):
        url = reverse('surveys:qgroup-answers-volume',
                      kwargs={'survey_id': 7, 'qgroup_id': 20})
        response = self.client.get(url, {'state': 'ka'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_groups', response.data)
        self.assertIn('volumes', response.data)
        self.assertEqual(
            response.data['volumes'][2016]['Aug'],
            len(ANSWERGROUP_INSTITUTION_IDS))
