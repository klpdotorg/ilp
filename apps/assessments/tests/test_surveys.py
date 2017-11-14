from django.urls import reverse
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory


class SurveysAPITests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/surveys')

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_list_surveys(self):
        url = reverse('surveys:surveys-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_detail_survey(self):
        url = reverse('surveys:surveys-detail', kwargs={'pk': 5})
        response = self.client.get(url)
        print("URL is -", url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
