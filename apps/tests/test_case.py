from rest_framework.test import APITestCase
from django.core.management import call_command

class IlpTestCase(APITestCase):
    
    @classmethod
    def setUpTestData(self):
        #Load fixtures
        print ("loading fixtures")
        call_command('loaddata', 'apps/tests/fixtures/common', verbosity=0)
        call_command('loaddata', 'apps/tests/fixtures/test_boundary', verbosity=0)
        call_command('creatematviews', verbosity=3)