from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from assessments.tests.test_fixtures.meta import (
    ANSWERGROUP_INSTITUTION_IDS
)


class AGroupInstitutionViewset(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/'
                      'answergroup_institution.json'))

    def test_answergroup_institution_list(self):
        url = reverse('assessment:answergroup_institution',
                      kwargs={'survey_id': 7})
        response = self.client.get(url, {'state': 'ka'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Parents', response.data['respondents'])
        self.assertEqual(response.data['total']['stories'],
                         len(ANSWERGROUP_INSTITUTION_IDS))
