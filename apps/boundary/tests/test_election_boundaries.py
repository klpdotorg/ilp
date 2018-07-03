from rest_framework.test import APITestCase, APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status
import json
import base64
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from tests import IlpTestCase
from boundary.api_views import (AssemblyBoundariesViewSet,
                                ParliamentBoundariesViewSet)


class ElectionBoundaryTests(APITestCase):

    @classmethod
    def setUpTestData(self):
        call_command('loaddata',
                     'apps/boundary/tests/test_fixtures/common',
                     verbosity=0)
        call_command('loaddata',
                     'apps/boundary/tests/test_fixtures/election_boundaries',
                     verbosity=0)

    def setUp(self):
       
        self.assemblylistView = AssemblyBoundariesViewSet.as_view(
            actions={'get': 'list'})
        self.assemblydetailView = AssemblyBoundariesViewSet.as_view(
            actions={'get': 'retrieve'})
        self.parliamentlistView = ParliamentBoundariesViewSet.as_view(
            actions={'get': 'list'})
        self.parliamentDetailView = ParliamentBoundariesViewSet.as_view(
            actions={'get': 'retrieve'})
        self.factory = APIRequestFactory()

    def test_list_assemblies(self):
        url = reverse('boundary:assemblyListView')
        request = self.factory.get(url, {'state': 'ka'})
        response = self.assemblylistView(request)
        response.render()
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data)

    def test_list_parliamentary_bounds(self):
        url = reverse('boundary:parliamentsListView')
        request = self.factory.get(url, {'state': 'ka'})
        response = self.parliamentlistView(request)
        response.render()
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data)
