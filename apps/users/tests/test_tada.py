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
       
    def setUp(self):
        pass

    def test_tada_auth_flow(self):
        url = reverse('user:tada-user-register')
        print("===========================")
        print("Testing user registration URL: ", url)
        print("===========================")
        response = self.client.post(
            url, {
                "email": "tadadeo1@klp.org.in",
                "mobile_no": "5555533321",
                "password": "sametime",
                "first_name": "Tada",
                "last_name": "DEO",
                "groups": ["tada_deo"],
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'groups', 'email', 'mobile_no', 'first_name', 'last_name', 'groups', 'is_active',
                'is_superuser']).issubset(response.data.keys())
        )
        self.assertTrue(response.data['is_active'])
        created_user_id = response.data['id']