from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from users.models import  User


class UserTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/users/tests/test_fixtures/auth_groups')
       
    def setUp(self):
        pass

    def test_user_auth_flow(self):
        url = reverse('user:user-register')
        print("===========================")
        print("Testing user registration URL: ", url)
        print("===========================")
        response = self.client.post(
            url, {
                "email": "test_user@klp.org.in",
                "mobile_no": "5555533321",
                "password": "sametime",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name']).issubset(response.data.keys())
        )
        created_user_id = response.data['id']
        
        # Retrieve the User object
        user = User.objects.get(id=created_user_id)
        verify_pin = user.sms_verification_pin
        mobile_no = user.mobile_no
        self.assertIsNotNone(verify_pin)
        self.verify_otp_password(mobile_no, verify_pin)

        #retrieve the user obejct again and check the status
        user = User.objects.get(id=created_user_id)
        self.assertTrue(user.is_active)
        print("User is now active")

        #Attempt login
        self.login(user.mobile_no, 'sametime')
        print("===========================")
        print("User auth flow test complete")
        print("===========================")

    def login(self, username, password):
        url = reverse('user:user-login')
        print("Attempting to login user with username %s" % username)
        response = self.client.post(url,
            {
                "username": username,
                "password": password
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("User successfully logged in")


    def verify_otp_password(self, mobile_no, pin):
        url = reverse('user:api_otp_update')
        print("Verifying user %s using PIN" % mobile_no)
        response = self.client.post(
            url, {
                "mobile_no": mobile_no,
                "otp": pin
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("User successfully verified")