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

    # setupTestData is invoked in the parent class
    # which sets up fixtures just once for all
    # the tests.
    # So this test case should essentially be just
    # reads/fetches. # If we require a pristine
    # DB each time for
    # writes, please write another class

    @classmethod
    def setUpTestData(self):
        # Load fixtures
        print("loading fixtures")
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/institution')
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/studentgroup')

    def setUp(self):
        # setup a test user
        self.user = get_user_model().objects.create_user(
            'admin@klp.org.in', 'admin')
        self.listView = StudentGroupViewSet.as_view(
            actions={'get': 'list'})
        self.detailView = StudentGroupViewSet.as_view(
            actions={'get': 'retrieve'})
        self.cudView = StudentGroupViewSet.as_view(
            actions={'post': 'create',
                     'put': 'update',
                     'patch': 'partial_update'})
        self.factory = APIRequestFactory()

    def test_list_studentgroups(self):
        url = reverse('institution:institution-studentgroup-list', kwargs={
            'parent_lookup_institution': '36172'})
        print("=======================================================")
        print("Test listing all student groups under institution - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.listView(request, parent_lookup_institution=36172,
                                 pk=36172)
        data = response.data
        print("Response is : ", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data)
        self.assertNotEqual(data['count'], 0)
        print("End test ===============================================")

    def test_getdetails_studentgroup(self):
        url = reverse('institution:institution-studentgroup-detail', kwargs={
            'parent_lookup_institution': '36172',
            'pk': '3486429'})
        print("=======================================================")
        print("Test getting student group details under institution - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.detailView(request, parent_lookup_institution=36172,
                                   pk=3486429)
        data = response.data
        print("Response is : ", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(data)
        # self.assertNotEqual(data['count'],0)
        print("End test ===============================================")

    def test_studentgroup_create(self):
        request = self.factory.post('/institution/studentgroups/', {
            'institution': '36172',
            'name': 'test_class_1A',
            'section': 'A',
            'group_type': 'class',
            'status': 'AC'}, format='json')
        response = self.cudView(request)
        response.render()
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'name', 'institution', 'status', 'group_type']).issubset
            (response.data.keys())
        )
        self.assertEqual(data['name'], 'test_class_1A')
        self.assertEqual(data['institution'], 36172)

    def test_studentgroup_partial_update(self):
        # Create a test student group first
        request = self.factory.post('/institution/studentgroups/', {
            'institution': '36172',
            'name': 'test_class_1A',
            'section': 'A',
            'group_type': 'class',
            'status': 'AC'}, format='json')
        response = self.cudView(request)
        response.render()
        data = response.data
        id = data['id']
        instId = data['institution']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Now update the student group
        request = self.factory.patch('/institution/' +
                                     str(instId) +
                                     '/studentgroups/' +
                                     str(id),
                                     {
                                         'name': 'test_updated_class_1A'},
                                     format='json')
        response = self.cudView(request, pk=id)
        response.render()
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'test_updated_class_1A')

    def test_studentgroup_update(self):
        # Create a test student group first
        request = self.factory.post('/institution/studentgroups/', {
            'institution': '36172',
            'name': 'test_class_1A',
            'section': 'A',
            'group_type': 'class',
            'status': 'AC'}, format='json')
        response = self.cudView(request)
        response.render()
        data = response.data
        id = data['id']
        inst_id = data['institution']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Now update the student group
        patch_data = {
            'name': 'test_updated_class_1A',
            'section': 'B',
            'institution': '36172',
            'group_type': 'class',
            'status': 'AC'
        }
        request = self.factory.patch(
            '/institution/' + str(inst_id) +
            '/studentgroups/' + str(id),
            patch_data, format='json'
        )
        response = self.cudView(request, pk=id)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], 'test_updated_class_1A')
        self.assertEqual(data['section'], 'B')
