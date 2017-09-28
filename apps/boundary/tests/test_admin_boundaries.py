from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
# Create your tests here.
from boundary.api_views import (Admin1sBoundary, Admin2sBoundary,
                                Admin3sBoundary,
                                Admin2sInsideAdmin1,
                                Admin3sInsideAdmin1,
                                Admin3sInsideAdmin2)


class AdminBoundaryApiTests(APITestCase):

    '''setupTestData is invoked in the parent class which sets up
     fixtures just once for all the tests.So this test case should
    essentially be just reads/fetches. If we require a pristine DB
    each time for writes, please write another class '''

    @classmethod
    def setUpTestData(self):
        '''Load fixtures'''
        print("loading fixtures")
        call_command('loaddata', 'apps/boundary/tests/test_fixtures/common',
                     verbosity=3)
        call_command('loaddata', 'apps/boundary/tests/ \
        test_fixtures/test_boundary',
                     verbosity=3)
        '''This is a custom django admin command created under boundary/
         management/commands.
        It can be used to create more matviews by modifying the py file '''
        call_command('creatematviews', verbosity=0)

    def setUp(self):
        '''setup a test user'''
        self.user = get_user_model().objects               .create_user(
            'admin',
            'admin@klp.org.in',
            'admin')
        self.view = Admin1sBoundary.as_view()
        self.admin2sView = Admin2sBoundary.as_view()
        self.admin3sView = Admin3sBoundary.as_view()
        self.admin2InsideAdmin1 = Admin2sInsideAdmin1.as_view()
        self.admin3InsideAdmin1 = Admin3sInsideAdmin1.as_view()
        self.admin3InsideAdmin2 = Admin3sInsideAdmin2.as_view()
        self.factory = APIRequestFactory()

    def test_list_noauth(self):
        url = reverse('boundary:admin1s-boundary')
        print("=======================================================")
        print("Test unauthorized access of URL - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        response.render()
        data = response.data
        print("Response is: ", data)
        print("End test ===============================================")

    def test_list_admin1s_boundaries(self):
        url = reverse('boundary:admin1s-boundary')
        print("=======================================================")
        print("Test listing all admin1s boundaries - ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertIsNotNone(data)
        self.assertNotEqual(data['count'], 0)
        self.assertEqual(data['count'], 6)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin1s_preschool_districts(self):
        url = reverse('boundary:admin1s-boundary')
        print("=======================================================")
        print("Testing listing admin1s boundaries filter by school type ", url)
        request = self.factory.get(url, {'state': 'ka', 'school_type': 'pre'})
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        # self.assertEqual(data['count'],4)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin1s_primaryschool_districts(self):
        url = reverse('boundary:admin1s-boundary')
        print("=======================================================")
        print("Testing listing primary school admin1s boundaries ", url)
        request = self.factory.get(
            url, {'state': 'ka', 'school_type': 'primary'})
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin2s_boundaries(self):
        url = reverse('boundary:admin2s-boundary')
        print("=======================================================")
        print("Testing list all admin2s boundaries ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.admin2sView(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        # self.assertEqual(data['count'],214)
        self.assertTrue(data['results'][0]['boundary_type'] == 'SB')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin2s_preschool_districts(self):
        url = reverse('boundary:admin2s-boundary')
        print("=======================================================")
        print("Testing listing admin2s preschool boundaries ", url)
        request = self.factory.get(url, {'state': 'ka', 'school_type': 'pre'})
        force_authenticate(request, user=self.user)
        response = self.admin2sView(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin2s_primaryschool_districts(self):
        url = reverse('boundary:admin2s-boundary')
        print("=======================================================")
        print("Testing listing primary school admin2s boundaries ", url)
        request = self.factory.get(
            url, {'state': 'ka', 'school_type': 'primary'})
        force_authenticate(request, user=self.user)
        response = self.admin2sView(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin3s_boundaries(self):
        url = reverse('boundary:admin3s-boundary')
        print("=======================================================")
        print("Testing list all admin3s boundaries ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.admin3sView(request, state='ka')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin3s_preschool_districts(self):
        url = reverse('boundary:admin3s-boundary')
        print("=======================================================")
        print("Testing listing admin3s preschool boundaries ", url)
        request = self.factory.get(url, {'state': 'ka', 'school_type': 'pre'})
        force_authenticate(request, user=self.user)
        response = self.admin3sView(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        self.assertTrue(data['results'][0]['boundary_type'] == 'PC')
        self.assertTrue(data['results'][0]['type'] == 'pre')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_admin3s_primaryschool_districts(self):
        url = reverse('boundary:admin3s-boundary')
        print("=======================================================")
        print("Testing listing primary school admin3s boundaries ", url)
        request = self.factory.get(
            url, {'state': 'ka', 'school_type': 'primary'})
        force_authenticate(request, user=self.user)
        response = self.admin3sView(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        print("Data count is: ", data['count'])
        self.assertTrue(data['count'] > 0)
        self.assertTrue(data['results'][0]['boundary_type'] == 'SC')
        self.assertTrue(data['results'][0]['type'] == 'primary')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_getadmin2s_admin1(self):
        url = '/api/v1/ka/boundary/admin1/414/admin2'
        print("=======================================================")
        print("Testing fetch admin2s boundaries for district ID: 414 ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.admin2InsideAdmin1(request, id=414)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        print("Response is : ", data)

        # Assert that blocks are returned and the parent is 414
        self.assertTrue(data['count'] > 0)
        self.assertTrue(data['results'][0]['boundary_type'] == 'SB')
        self.assertTrue(data['results'][0]['parent'] == 414)
        print("End test ===============================================")

    def test_getadmin3s_admin1(self):
        url = '/api/v1/ka/boundary/admin1/414/admin3'
        print("=======================================================")
        print("Testing fetch admin3s boundaries for district ID: 414 ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.admin3InsideAdmin1(request, id=414)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        self.assertTrue(data['count'] > 0)
        self.assertTrue(data['results'][0]['boundary_type'] == 'SC')
        print("Response is : ", data)
        print("End test ===============================================")

    def test_getadmin3s_admin2(self):
        url = '/api/v1/ka/boundary/admin2/467/admin3'
        print("=======================================================")
        print("Testing fetch admin2s boundaries for district ID: 467 ", url)
        request = self.factory.get(url, {'state': 'ka'})
        force_authenticate(request, user=self.user)
        response = self.admin3InsideAdmin2(request, id=467)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.render()
        data = response.data
        print("Response is : ", data)
        # Assert that blocks are returned and the parent is 467
        self.assertTrue(data['count'] > 0)
        self.assertTrue(data['results'][0]['boundary_type'] == 'SC')
        self.assertTrue(data['results'][0]['parent'] == 467)
        print("End test ===============================================")
