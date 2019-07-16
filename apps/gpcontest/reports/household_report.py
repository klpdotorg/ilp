from assessments.models import (
    SurveyEBoundaryQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    Question
    )

def getHouseholdSurvey(survey_id,boundary,date_range):
        """ Returns household survey aggregate values in a dictionary per boundary """

        hh_answers_agg = None
        HHSurvey = []

        if isinstance(boundary, ElectionBoundary):
            try:
                hh_answers_agg = SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(eboundary_id=boundary)\
                    .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])\
                    .filter(question_id__in=self.hh_question_ids)
            except SurveyEBoundaryQuestionGroupAnsAgg.DoesNotExist:
                print("No community survey data for '{}' between {} and {}".format(boundary.const_ward_name, self.report_from, self.report_to))
        else:
        #Household Survey
            hh_answers_agg = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=boundary)\
                .filter(yearmonth__range=date_range,questiongroup_id__in=self.hh_questiongroup_ids)\
                .filter(question_id__in=self.hh_question_ids)
        if hh_answers_agg is not None and hh_answers_agg.exists():
            total_hh_answers = hh_answers_agg.values('question_desc', 'question_id').annotate(Sum('num_answers'))
            total_yes_answers = hh_answers_agg.filter(answer_option='Yes').values('question_desc', 'question_id').annotate(Sum('num_answers'))
            for each_answer in total_hh_answers:
                question_desc = total_yes_answers.get(question_desc=each_answer['question_desc'])
                total_yes_count = question_desc['num_answers__sum']
                question_text = Question.objects.get(id=each_answer['question_id']).question_text
                HHSurvey.append({'text':question_text,'percentage': "{:.2f}".format(round((total_yes_count/each_answer['num_answers__sum'])*100, 2))})
        else:
             print("No community survey data for '{}' between {} and {}".format(boundary.name, self.report_from, self.report_to))
        return HHSurvey

def getAllHouseHoldSurveyReports()