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
# Create your tests here.
from boundary.api_views import (Admin1sBoundary, Admin2sBoundary, Admin3sBoundary,
                        Admin2sInsideAdmin1, Admin3sInsideAdmin1, 
                        Admin3sInsideAdmin2)
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
        call_command('creatematviews', verbosity=3)

    def setUp(self):
        #setup a test user
        self.user = get_user_model().objects.create_user('admin', 'admin@klp.org.in', 'admin')
        self.view = Admin1sBoundary.as_view()
        self.admin2sView = Admin2sBoundary.as_view()
        self.admin3sView = Admin3sBoundary.as_view()
        self.admin2InsideAdmin1 = Admin2sInsideAdmin1.as_view()
        self.admin3InsideAdmin1 = Admin3sInsideAdmin1.as_view()
        self.admin3InsideAdmin2 = Admin3sInsideAdmin2.as_view()
        self.factory = APIRequestFactory()
        # country, created = BoundaryType.objects.get_or_create(char_id="C", name="Country")
        # state, created = BoundaryType.objects.get_or_create(char_id="ST", name="State")
        # school_district, created = BoundaryType.objects.get_or_create(char_id="SD", name="School District")
        # preschool_district, created = BoundaryType.objects.get_or_create(char_id="PD", name="Preschool District")


        # active_status, created = Status.objects.get_or_create(char_id="AC", name="Active")

        # preschool_type, created = InstitutionType.objects.get_or_create(char_id="pre",name="Preschool")
        # primary_type, created = InstitutionType.objects.get_or_create(char_id="primary", name="Primary School")

        # boundary_india, created = Boundary.objects.get_or_create(id=1,name="India", boundary_type=country, dise_slug="India",status=active_status)
        # boundary_karnataka, created = Boundary.objects.get_or_create(id=2,parent=boundary_india,name="Karnataka", boundary_type=state, dise_slug="Karnataka",status=active_status)
        # Boundary.objects.get_or_create(id=3, parent=boundary_karnataka, name="Test District",boundary_type=school_district, type=preschool_type, dise_slug="Test District", status=active_status)
    

    def test_print(self):
        print("Testing print...")
        pass
        boundaries = Boundary.objects.all()
        print("Boundaries exist, ", boundaries)
    def test_list_noauth(self):
        url = reverse('admin1s-boundary', kwargs={'state':'ka'})
        print("=======================================================")
        print("Test unauthorized access of URL - ",url)
        request = self.factory.get(url)
        response = self.view(request, state='ka')
        self.assertEqual(response.status_code,200)
        response.render()
        data = json.loads(response.content)
        print("Response is: ", data)
        print("End test ===============================================")
       
    def test_list_admin1s_boundaries(self):
        url = reverse('admin1s-boundary', kwargs={'state':'ka'})
        print("=======================================================")
        print("Test listing all admin1s boundaries - ", url)
        request = self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.view(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertIsNotNone(data)
        self.assertNotEqual(data['count'],0)
        self.assertEqual(data['count'],38)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin1s_preschool_districts(self):
        url=reverse('admin1s-boundary', kwargs={'state': 'ka'})
        url=url + '?school_type=pre'
        print("=======================================================")
        print("Testing listing admin1s boundaries filter by school type ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.view(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertEqual(data['count'],4)
        print("Response is : ", data)
        print("End test ===============================================")
    
    def test_admin1s_primaryschool_districts(self):
        url=reverse('admin1s-boundary', kwargs={'state': 'ka'})
        url = url + '?school_type=primary'
        print("=======================================================")
        print("Testing listing primary school admin1s boundaries ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.view(request,state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'], 34)
        print("Response is : ", data)
        print("End test ===============================================")
    
    def test_admin2s_boundaries(self):
        url=reverse('admin2s-boundary', kwargs={'state': 'ka'})
        #url = '/api/v1/ka/boundary/admin2s'
        print("=======================================================")
        print("Testing list all admin2s boundaries ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin2sView(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'],214)
        self.assertTrue(data['results'][0]['boundary_type']== 'SB')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin2s_preschool_districts(self):
        url=reverse('admin2s-boundary', kwargs={'state': 'ka'})
        url = url + '?school_type=pre'
        print("=======================================================")
        print("Testing listing admin2s preschool boundaries ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin2sView(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'], 11)
        print("Response is : ", data)
        print("End test ===============================================")
    
    def test_admin2s_primaryschool_districts(self):
        url = reverse('admin2s-boundary', kwargs={'state': 'ka'})
        url = url + '?school_type=primary'
        print("=======================================================")
        print("Testing listing primary school admin2s boundaries ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin2sView(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'], 203)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin3s_boundaries(self):
        url = reverse('admin3s-boundary', kwargs={'state': 'ka'})
        print("=======================================================")
        print("Testing list all admin3s boundaries ", url)
        request = self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin3sView(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'], 4212)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin3s_preschool_districts(self):
        url = reverse('admin3s-boundary', kwargs={'state': 'ka'})
        url = url + '?school_type=pre'
        print("=======================================================")
        print("Testing listing admin3s preschool boundaries ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin3sView(request,state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'],151)
        self.assertTrue(data['results'][0]['boundary_type']== 'PC')
        self.assertTrue(data['results'][0]['type']=='pre')
        print("Response is : ", data)
        print("End test ===============================================")
    
    def test_admin3s_primaryschool_districts(self):
        url = reverse('admin3s-boundary', kwargs={'state': 'ka'})
        url = url + '?school_type=primary'
        print("=======================================================")
        print("Testing listing primary school admin3s boundaries ", url)
        request = self.factory.get(url)
        force_authenticate(request,user=self.user)
        response = self.admin3sView(request, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        print("Data count is: ", data['count'])
        self.assertTrue(data['count']>0)
        self.assertEqual(data['count'],4061)
        self.assertTrue(data['results'][0]['boundary_type']== 'SC')
        self.assertTrue(data['results'][0]['type']=='primary')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_getadmin2s_admin1(self):
        url='/api/v1/ka/boundary/admin1/414/admin2'
        print("=======================================================")
        print("Testing fetch admin2s boundaries for district ID: 414 ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response=self.admin2InsideAdmin1(request,id=414, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        print("Response is : ", data)

        '''Assert that blocks are returned and the parent is 414'''
        self.assertTrue(data['count']>0)
        self.assertTrue(data['results'][0]['boundary_type']== 'SB')
        self.assertTrue(data['results'][0]['parent']==414)
        print("End test ===============================================")
    
    def test_getadmin3s_admin1(self):
        url='/api/v1/ka/boundary/admin1/414/admin3'
        print("=======================================================")
        print("Testing fetch admin3s boundaries for district ID: 414 ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response=self.admin3InsideAdmin1(request,id=414, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        self.assertTrue(data['count']>0)
        self.assertTrue(data['results'][0]['boundary_type']== 'SC')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_getadmin3s_admin2(self):
        url='/api/v1/ka/boundary/admin2/467/admin3'
        print("=======================================================")
        print("Testing fetch admin2s boundaries for district ID: 467 ", url)
        request=self.factory.get(url)
        force_authenticate(request,user=self.user)
        response=self.admin3InsideAdmin2(request, id=467, state='ka')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response.render()
        data = json.loads(response.content)
        print("Response is : ", data)
        '''Assert that blocks are returned and the parent is 467'''
        self.assertTrue(data['count']>0)
        self.assertTrue(data['results'][0]['boundary_type']== 'SC')
        self.assertTrue(data['results'][0]['parent']==467)
        print("End test ===============================================")