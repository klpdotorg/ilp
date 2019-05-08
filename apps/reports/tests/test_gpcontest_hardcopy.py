from django.core.management import call_command
from rest_framework import status
from django.test import TestCase
from reports.gp_hardcopy_reports.compute_numbers import *

class GPContestReportsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata',
                     'apps/reports/tests/fixtures/answers')
        call_command('loaddata',
                     'apps/reports/tests/fixtures/competencymap')
        call_command('run_materialized_view')

    
    def test_compute_numbers(self):
        score_agg = get_gradewise_score_buckets(1035, [45,46,47])
        print(score_agg)
            # if item['answergroup__questiongroup_id'] == 45:
            #     self.assertEqual(item['percent_score'], 30.0)
            # elif item['answergroup__questiongroup_id'] == 46:
            #     self.assertEqual(item['percent_score'],5.0)
    
    def test_get_correctans_agg(self):
        answers = get_competency_scores(1035, 2, 201806, 201903)
        print("printing results")
        for item in answers:
            print(item)

