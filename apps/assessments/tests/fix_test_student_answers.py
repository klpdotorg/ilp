from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
import json

from assessments.tests.test_fixtures.meta import (
    TEST_ANSWERGROUP_POST_DATA
)

class StudentAnswersApiTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/surveys')
        call_command('loaddata',
                     'apps/assessments/tests/test_fixtures/respondenttype')
        # call_command('loaddata',
        #              'apps/assessments/tests/test_fixtures/users')
        call_command('loaddata',
                      'apps/assessments/tests/test_fixtures/answer_student')

    def setUp(self):
        # setup a test user
        self.user = get_user_model().objects.create_superuser(
            '3322233323', 'admin')
        self.base_url = '/api/v1/surveys/3/questiongroup/31/student/2112477/'
        self.post_answers = {
                             "questiongroup":31,"student":2112477,"group_value":"Subhashini",
                             "created_by":2,
                             "date_of_visit":"2016-12-09T14:20:01.211000Z","respondent_type":"VR",
                             "comments":"Test comment","is_verified":True,"status":"AC",
                             "answers":[
                             {"question":393,"answer":"1"},
                             {"question":394,"answer":"1"},
                             {"question":395,"answer":"0"},
                             {"question":396,"answer":"0"},
                             {"question":397,"answer":"0"},
                             {"question":437,"answer":"0"},
                             {"question":438,"answer":"1"},
                             {"question":443,"answer":"1"}]}
                             # {"id":9,"question":401,"answer":"0","answergroup":1,"double_entry":null},{"id":10,"question":405,"answer":"1","answergroup":1,"double_entry":null}'

    def test_answer_create(self):
        self.client.force_authenticate(user=self.user)
        json_data = json.dumps(self.post_answers)
        response = self.client.post(self.base_url + 'answers/',
                                    json_data,content_type='application/json')
        data = response.data
        # import ipdb ; ipdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print("Response is: ",data)
        self.assertTrue(
            set(['id', 'questiongroup', 'student', 'group_value',
                'created_by', 'date_of_visit', 'respondent_type', 'answers']).issubset(response.data.keys())
        )
        self.assertTrue(len(data['answers']) >0)
    
    def test_answers_list(self):
        response = self.client.get(self.base_url+ 'answergroup/1/answers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_answers_patch(self):
        # First create the answer
        self.client.force_authenticate(user=self.user)
        json_data = json.dumps(self.post_answers)
        response = self.client.post(self.base_url + 'answers/',
                                    json_data,content_type='application/json')
        data = response.data
        # import ipdb ; ipdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            set(['id', 'double_entry', 'questiongroup', 'student', 'group_value',
                'created_by', 'date_of_visit', 'respondent_type', 'answers']).issubset(response.data.keys())
        )
        self.assertTrue(len(data['answers']) >0)
        ansgroup_id = data['id']
        edit_answer = data['answers'][0]
        edit_answer_id = edit_answer['id']
        #Now patch it
        patched_answer = {'answer': 'No'}
        url = self.base_url + 'answergroup/' + str(ansgroup_id) + '/answers/' + str(edit_answer_id)+'/'
        response = self.client.patch(url,
                                    json.dumps(patched_answer),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(['id', 'answer', 'question', 'answergroup']).issubset(response.data.keys()))
        self.assertEquals(response.data['answer'], "No")

    def test_answergroup_list(self):
        response = self.client.get(self.base_url+'answergroup/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_answergroup_patch(self):
        self.client.force_authenticate(user=self.user)
        patch_url = self.base_url + 'answergroup/1/'
        response = self.client.patch(patch_url, 
                                    '{"respondent_type": "PR"}',
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(set(['respondent_type']).issubset(response.data.keys()))
        self.assertEqual(response.data['respondent_type'], 'PR')

    def test_add_answer_existing_answergrp(self):
        self.client.force_authenticate(user=self.user)
        new_answer= {'answers': [{'question': 401, 'answer': 0}]}
        response = self.client.post(self.base_url + 'answergroup/1/answers/', 
                                    json.dumps(new_answer),
                                    content_type='application/json')
        print("Adding answer to existing answer group: ",response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(set(['answers']).issubset(response.data.keys()))
        self.assertTrue(len(response.data['answers']) >0)
        for answer in response.data['answers']:
            if(answer['question'] == 401):
                self.assertEqual(int(answer['question']),401)
                self.assertEqual(int(answer['answer']),0)
    

   
