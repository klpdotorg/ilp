from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import json

from assessments.tests.test_fixtures.meta import (
    TEST_ANSWERGROUP_POST_DATA
)

class AnswersApiTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/surveys')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/respondenttype')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/users')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/institution_4464')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/qgroup_21_questions')              
    def setUp(self):
        # setup a test user
        self.user = get_user_model().objects.create(
            'admin@klp.org.in', 'admin')

    def test_answer_create(self):
        self.client.force_authenticate(user=self.user)
        json_data = json.dumps(TEST_ANSWERGROUP_POST_DATA)
        print("JSON data is: ", json_data)
        response = self.client.post('/api/v1/surveys/2/qgroup/21/institution/4464/answers/',
                                    json_data,content_type='application/json')
        print(response.data)
       

        data = response.data
        # import ipdb ; ipdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'double_entry', 'questiongroup', 'institution', 'group_value',
                'created_by', 'date_of_visit', 'respondent_type', 'answers']).issubset(response.data.keys())
        )
        self.assertTrue(len(data['answers']) >0)
