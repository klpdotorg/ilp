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
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/qgroup_questions') 
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/answergroup_institution')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/answer_institution')               
    def setUp(self):
        # setup a test user
        self.user = get_user_model().objects.create_superuser(
            '3322233323', 'admin')

    def test_answer_create(self):
        self.client.force_authenticate(user=self.user)
        json_data = json.dumps(TEST_ANSWERGROUP_POST_DATA)
        response = self.client.post('/api/v1/surveys/2/qgroup/21/institution/4464/answers/',
                                    json_data,content_type='application/json')
        data = response.data
        # import ipdb ; ipdb.set_trace()
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'double_entry', 'questiongroup', 'institution', 'group_value',
                'created_by', 'date_of_visit', 'respondent_type', 'answers']).issubset(response.data.keys())
        )
        self.assertTrue(len(data['answers']) >0)
    
    def test_answers_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/surveys/7/qgroup/20/institution/3895/answergroup/266252/answers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_answers_patch(self):
        # First create the answer
        self.client.force_authenticate(user=self.user)
        json_data = json.dumps(TEST_ANSWERGROUP_POST_DATA)
        response = self.client.post('/api/v1/surveys/2/qgroup/21/institution/4464/answers/',
                                    json_data,content_type='application/json')
        data = response.data
        # import ipdb ; ipdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'double_entry', 'questiongroup', 'institution', 'group_value',
                'created_by', 'date_of_visit', 'respondent_type', 'answers']).issubset(response.data.keys())
        )
        self.assertTrue(len(data['answers']) >0)
        ansgroup_id = data['id']
        edit_answer = data['answers'][0]
        edit_answer_id = edit_answer['id']
        #Now patch it
        patched_answer = {'answer': 'No'}
        url = '/api/v1/surveys/2/qgroup/21/institution/4464/answergroup/' + str(ansgroup_id) + '/answers/' + str(edit_answer_id)+'/'
        response = self.client.patch(url,
                                    json.dumps(patched_answer),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(['id', 'answer', 'question', 'answergroup']).issubset(response.data.keys()))    

    def test_answergroup_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/surveys/7/qgroup/20/institution/3895/answergroup/266252/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_answergroup_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch('/api/v1/surveys/7/qgroup/20/institution/3895/answergroup/266252/', 
                                    '{"respondent_type": "PR"}',
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(['respondent_type']).issubset(response.data.keys()))
        self.assertEqual(response.data['respondent_type'], 'PR')

    def test_add_answer_existing_answergrp(self):
        self.client.force_authenticate(user=self.user)
        new_answer= {'answers': [{'question': 145, 'answer': 'Yes'}]}
        response = self.client.post('/api/v1/surveys/7/qgroup/20/institution/3895/answergroup/266261/answers/', 
                                    json.dumps(new_answer),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    

   
