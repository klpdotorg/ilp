from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth import get_user_model

from assessments.models import QuestionGroup

from rest_framework import status
from rest_framework.test import APITestCase

from assessments.tests.test_fixtures.meta import (
    QUESTIONGROUP_ID, QUESTIONGROUP_QUESTION_COUNT, QUESTIONGROUP_QTYPE
)


class QuestionGroupQuestionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     ('apps/assessments/tests/test_fixtures/qgroup_questions'))

    def setUp(self):
        self.user = get_user_model().objects.create(
            'admin@klp.org.in', 'admin')
        self.test_survey_id = \
            QuestionGroup.objects.get(id=QUESTIONGROUP_ID).survey_id

    def test_surveys_questiongroup_list(self):
        url = reverse(
            'surveys:surveys-questiongroup-list',
            kwargs={'parent_lookup_survey': self.test_survey_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_surveys_questiongroup_detail(self):
        url = reverse(
            'surveys:surveys-questiongroup-detail',
            kwargs={'parent_lookup_survey': self.test_survey_id,
                    'pk': QUESTIONGROUP_ID}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], QUESTIONGROUP_ID)

    def test_surveys_questiongroup_question_list(self):
        url = reverse(
            'surveys:surveys-questiongroup-questions-list',
            kwargs={'parent_lookup_survey': self.test_survey_id,
                    'parent_lookup_questiongroup': QUESTIONGROUP_ID}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], QUESTIONGROUP_QUESTION_COUNT)

    def test_surveys_questiongroup_question_post(self):
        url = reverse(
            'surveys:surveys-questiongroup-questions-list',
            kwargs={'parent_lookup_survey': self.test_survey_id,
                    'parent_lookup_questiongroup': QUESTIONGROUP_ID}
        )
        post_data = {
            "question_details": {
                "question_text": "Is this a A, B or C grade school based on your observations?",
                "display_text": "How are the schools in this boundary rated?",
                "key": "ivrss-grade",
                "question_type_id": QUESTIONGROUP_QTYPE,
                "is_featured": True,
                "status": "AC"
            }
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'], QUESTIONGROUP_QUESTION_COUNT + 1)
