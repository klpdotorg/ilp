from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from schools.tests.test_fixtures.meta import INSTITUTION_COUNT


class InstitutionAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/institution')
        call_command('loaddata', 'apps/common/fixtures/institutiongender')
        call_command('loaddata', 'apps/common/fixtures/status')
        call_command('loaddata', 'apps/common/fixtures/institutiontype')
        call_command('creatematviews')

    def test_list_api(self):
        url = reverse('institution:basic-list')
        response = self.client.get(url, {'state': 'ka'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], INSTITUTION_COUNT)

    def test_list_api_with_geometry(self):
        url = reverse('institution:basic-list')
        response = self.client.get(url, {'state': 'ka', 'geometry': 'yes'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            set(['type', 'count', 'results']).issubset(response.data.keys())
        )
        results = response.data['results']
        self.assertTrue(
            set(['type', 'geometry', 'properties']).issubset(results[0].keys())
        )

    def test_list_api_admin_filters(self):
        # test admin1 filter
        url = reverse('institution:basic-list')
        response = self.client.get(url, {'state': 'ka', 'admin1': '0101'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test admin2 filter
        url = reverse('institution:basic-list')
        response = self.client.get(url, {'state': 'ka', 'admin2': '0101'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test admin2 filter
        url = reverse('institution:basic-list')
        response = self.client.get(url, {'state': 'ka', 'admin3': '0101'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_institution(self):
        url = reverse('institution:basic-list')
        response = self.client.post(
            url, {
                "name": "GULPS EMMIGANUR",
                "languages": "1",
                "admin3": 8829,
                "gender": "co-ed",
                "category": "10",
                "institution_type": "primary",
                "management": "1",
                "status": "AC"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
