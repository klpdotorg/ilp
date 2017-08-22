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
from boundary.api_views import (BoundaryViewSet)
from boundary.models import Boundary, BoundaryType
from common.models import Status, InstitutionType


class BoundaryApiTests(APITestCase):

    '''setupTestData is invoked in the parent class which sets up fixtures just once for all the tests.
    So this test case should essentially be just reads/fetches. If we require a pristine DB each time for
    writes, please write another class '''

    @classmethod
    def setUpTestData(self):
        #Load fixtures
        print("loading fixtures")
        call_command('loaddata', 'apps/boundary/tests/test_fixtures/common', 
                     verbosity=3)
        call_command('loaddata', 'apps/boundary/tests/test_fixtures/test_boundary', 
                     verbosity=3)
        '''This is a custom django admin command created under boundary/
         management/commands.
        It can be used to create more matviews by modifying the py file '''
        call_command('creatematviews', verbosity=0)

    def setUp(self):
        #setup a test user
        self.user = get_user_model().objects.create_user('admin', 'admin@klp.org.in', 'admin')
        self.listView = BoundaryViewSet.as_view(actions={'get': 'list'})
        self.detailView = BoundaryViewSet.as_view(actions={'get': 'retrieve'})
        self.factory = APIRequestFactory()
    
    def test_boundary_list(self):
        pass
