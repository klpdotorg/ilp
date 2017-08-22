from rest_framework.test import APITestCase, APIClient
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status
import json
import base64
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from tests import IlpTestCase
# Create your tests here.
from schools.api_view import (StudentGroupViewSet)
from boundary.models import Boundary, BoundaryType
from common.models import Status, InstitutionType


class StudentGroupApiTests(APITestCase):

    '''setupTestData is invoked in the parent class which sets up fixtures just once for all the tests.
    So this test case should essentially be just reads/fetches. If we require a pristine DB each time for
    writes, please write another class '''

    @classmethod
    def setUpTestData(self):
        #Load fixtures
        print("loading fixtures")
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/institution')
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/studentgroup')
        #call_command('run_materialized_view')

    def setUp(self):
        #setup a test user
        self.user = get_user_model().objects.create_user('admin', 'admin@klp.org.in', 'admin')
        self.listView = StudentGroupViewSet.as_view(actions={'get': 'list'})
        self.detailView = StudentGroupViewSet.as_view(actions={'get': 'retrieve'})
        self.factory = APIRequestFactory()

   
    def test_list_studentgroups(self):
        url = reverse('institution:studentgroup-list', kwargs={'parent_lookup_institution': '36172'})
        print("=======================================================")
        print("Test listing all student groups under institution - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request,user=self.user)
        response = self.listView(request, parent_lookup_institution=36172, pk=36172)
        response.render()
        data = json.loads(response.content)
        print("Response is : ", data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIsNotNone(data)
        self.assertNotEqual(data['count'],0)
        print("End test ===============================================")

    def test_getdetails_studentgroup(self):
        url = reverse('institution:studentgroup-detail', kwargs={'parent_lookup_institution': '36172', 'pk': '3486429'})
        print("=======================================================")
        print("Test getting student group details under institution - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request,user=self.user)
        response = self.detailView(request, parent_lookup_institution=36172, pk=3486429)
        response.render()
        data = json.loads(response.content)
        print("Response is : ", data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertIsNotNone(data)
        #self.assertNotEqual(data['count'],0)
        print("End test ===============================================")