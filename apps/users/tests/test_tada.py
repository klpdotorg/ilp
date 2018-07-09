from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import  User


class TadaUserTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/users/tests/test_fixtures/auth_groups')
        call_command('loaddata',
                     'apps/users/tests/test_fixtures/users')
       
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            '3322233323', 'admin')
        self.regular_user = get_user_model().objects.create('1223223221', 'regular')


    def registerUser(self):
        url = "/api/v1/tada/users/"
        print("URL is -- ", url)
        return self.client.post(
            url, {
                "email": "tadadeo1@klp.org.in",
                "mobile_no": "5555533321",
                "password": "sametime",
                "first_name": "Tada",
                "last_name": "DEO",
                "groups": ["tada_deo"],
            }
        )
    
    def loginUser(self, username, password):
        url = reverse('user:tada-user-login')
        print("Logging into -- ", url)
        print("Attempting to login TADA user with username %s" % username)
        response = self.client.post(url,
            {
                "username": username,
                "password": password
            }
        )
        return response

    def test_admin_create_user(self):
        print("===========================")
        print("Testing user registration")
        print("===========================")
        self.client.force_authenticate(user=self.user)
        response = self.registerUser()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        self.assertTrue(response.data['is_active'])
        created_user_id = response.data['id']
        print("Registration response is: ", response.data)
        #Retrieve the user and check
        response = self.client.get("/api/v1/tada/users/"+str(created_user_id)+"/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )

    def test_failing_register(self):
        print("===========================")
        print("Testing unauthorized user registration")
        print("===========================")
        self.client.force_authenticate(user=self.regular_user)

        response = self.registerUser()
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_login(self):
        # Create user first        
        print("===========================")
        print("Testing TADA user login")
        print("===========================")
       
        self.client.force_authenticate(user=self.user)
        response = self.registerUser()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        mobile_no = response.data['mobile_no']

        # Now login
        response = self.loginUser(mobile_no, 'sametime')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("User successfully logged in")

        # Check user profile
        url = reverse('user:api_user_profile')
        print("Retrieving user profile - ", url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)

    """ This method tests a user updating his/her own profile"""
    def test_self_update_user_profile(self):
        print("===========================")
        print("Testing user profile update")
        print("===========================")
       
        self.client.force_authenticate(user=self.user)
        response = self.registerUser()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        mobile_no = response.data['mobile_no']

        # Now login
        response = self.loginUser(mobile_no, 'sametime')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("User successfully logged in")

        # Check user profile
        created_user = User.objects.get(id=response.data['id'])
        self.client.force_authenticate(user=created_user)
        url = reverse('user:api_user_profile')
        response = self.client.patch(url, {
            "first_name": "Firstname",
            "last_name": "Lastname"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("User profile updated successfully -- ", response.data)
        self.assertTrue(
            set(['first_name', 'last_name']).issubset(response.data.keys())
        )
        self.assertEqual(response.data['first_name'], "Firstname")
        self.assertEqual(response.data['last_name'], "Lastname")
    
    def test_admin_list_users(self):
        url = reverse('user:tada-users-list')
        print("Testing listing users %s" % url)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data['count'], 3)
        print("Listing users: ", response.data)
    
    def test_nonadmin_list_users(self):
        url = reverse('user:tada-users-list')
        print("Testing listing users %s" % url)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # User 21002 is in the text_fixtures/users.json file
    def test_admin_user_detail(self):
        url = reverse('user:tada-users-detail',kwargs={'pk': '21002'})
        print("Testing user details %s" % url)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        self.assertEqual(response.data['id'], 21002)
    
    # User 21002 is in the text_fixtures/users.json file
    def test_nonadmin_user_detail(self):
        url = reverse('user:tada-users-detail',kwargs={'pk': '21002'})
        print("Testing user details %s" % url)
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
      
    
    def test_user_delete(self):
        print("===========================")
        print("Testing user deletion")
        print("===========================")
       
        self.client.force_authenticate(user=self.user)
        response = self.registerUser()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        id = response.data['id']

        url = reverse('user:tada-users-detail',kwargs={'pk': id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_nonadmin_user_delete(self):
        print("===========================")
        print("Testing NON-ADMIN user deletion")
        print("===========================")
       
        self.client.force_authenticate(user=self.user)
        response = self.registerUser()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        id = response.data['id']

        url = reverse('user:tada-users-detail',kwargs={'pk': id})
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_view_user_profile(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user:api_user_profile')
        print("=========================")
        print("Retrieving User Profile")
        print("=========================")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        print(response.data)



