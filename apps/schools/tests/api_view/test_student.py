from django.urls import reverse
from django.core.management import call_command

from rest_framework import status
from rest_framework.test import APITestCase

from schools.tests.test_fixtures.meta import (
    INSTITUTION_ID_2, STUDENTGROUP_ID, STUDENT_COUNT
)


class StudentAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        print("loading fixtures")
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/institution')
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/studentgroup')
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/student')
        call_command('loaddata',
                     'apps/schools/tests/test_fixtures/studentgrouprelation')

    # def test_student_create(self):
    #     url = reverse('institution:institution-studentgroup-student-list',
    #                   kwargs={'parent_lookup_institution': INSTITUTION_ID_2,
    #                           'parent_lookup_studentgroups': STUDENTGROUP_ID})
    #     response = self.client.get(url, {'state': 'ka'})

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(
    #         response.data['count'], STUDENT_COUNT
    #     )
