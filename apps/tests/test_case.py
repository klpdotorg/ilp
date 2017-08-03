from rest_framework.test import APITestCase
from django.core.management import call_command

class IlpTestCase(APITestCase):
    
    @classmethod
    def setUpTestData(self):
        #Load fixtures
        print ("loading fixtures")
        call_command('loaddata', 'apps/tests/test_fixtures/common', verbosity=0)
        call_command('loaddata', 'apps/tests/test_fixtures/test_boundary', verbosity=0)
        '''This is a custom django admin command created under boundary/
         management/commands.
        It can be used to create more matviews by modifying the py file '''
        call_command('creatematviews', verbosity=3)