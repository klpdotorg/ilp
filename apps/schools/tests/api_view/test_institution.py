from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from schools.tests.fixtures.meta import INSTITUTION_COUNT


class InstitutionAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', 'apps/schools/tests/fixtures/institution')

    def test_list_api(self):
        url = reverse('institution-list', kwargs={'state': 'ka'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], INSTITUTION_COUNT)

    def test_list_api_with_geometry(self):
        url = (
            reverse('institution-list', kwargs={'state': 'ka'}) +
            "?geometry=yes"
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            set(['type', 'count', 'results']).issubset(response.data.keys())
        )
        results = response.data['results']
        self.assertTrue(
            set(['type', 'geometry', 'properties']).issubset(results[0].keys())
        )
