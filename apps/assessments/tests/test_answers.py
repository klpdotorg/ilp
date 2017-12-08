from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.tests.test_fixtures.meta import (
    TEST_ANSWERGROUP_POST_DATA
)

class AnswersApiTests(APITestCase):

    def setUp(self):
        # setup a test user
        self.user = get_user_model().objects.create(
            'admin@klp.org.in', 'admin')

    def test_answer_create(self):
            self.client.force_authenticate(user=self.user)
            response = self.client.post('/api/v1/survey/2/qgroup/21/institution/4464/answers/',
                                        TEST_ANSWERGROUP_POST_DATA, format='json')
            print(response)
            data = response.data
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # self.assertTrue(
            #     set(['id', 'name', 'parent', 'dise_slug', 'boundary_type',
            #         'type', 'status']).issubset(response.data.keys())
            # )
            # self.assertEqual(data['name'], 'test_SD')
            # self.assertEqual(data['boundary_type'], 'SD')