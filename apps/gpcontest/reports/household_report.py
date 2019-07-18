from assessments.models import (
    SurveyEBoundaryQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    Question,
    QuestionGroup_Questions
    )
from boundary.models import (
    Boundary, ElectionBoundary
)
from django.db.models import Sum

def getHouseholdSurvey(survey_id,boundary_id,date_range):
        """ Returns household survey aggregate values in a dictionary per boundary """
        boundary = None
        # Boundary has to be a Boundary or ElectionBoundary
        try:
            boundary = Boundary.objects.get(id=boundary_id)
        except:
            boundary = ElectionBoundary.objects.get(id=boundary_id)
        hh_answers_agg = None
        HHSurvey = {}
        answers = []
        boundary_type = None
        if boundary is not None:
            boundary_type = ""
            boundary_name = ""
            if isinstance(boundary, ElectionBoundary):
                boundary_type = boundary.const_ward_type_id
                boundary_name = boundary.const_ward_name
                try:
                    hh_answers_agg = SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(eboundary_id=boundary)\
                        .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])
                except SurveyEBoundaryQuestionGroupAnsAgg.DoesNotExist:
                    print("No community survey data for '{}' between {} and {}".format(boundary.const_ward_name, date_range))
            else:
                #Household Survey
                boundary_type = boundary.boundary_type_id
                boundary_name = boundary.name
                hh_answers_agg = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=boundary)\
                    .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])
            if hh_answers_agg is not None and hh_answers_agg.exists():
                HHSurvey['boundary_name'] = boundary_name
                HHSurvey['boundary_type'] = boundary_type
                total_hh_answers = hh_answers_agg.values('question_id').annotate(Sum('num_answers'))
                total_yes_answers = hh_answers_agg.filter(answer_option='Yes').values('question_id').annotate(Sum('num_answers'))
                ordered_list = QuestionGroup_Questions.objects.filter(questiongroup_id__in=[18, 20]).order_by('sequence', 'question_id').distinct('sequence', 'question_id').values_list('question_id', flat=True)
                ordered_list = list(ordered_list)
                print(ordered_list)
                sorted_questions = sorted(total_hh_answers, key=lambda q: ordered_list.index(q['question_id']))
                #print(sorted_questions.values_list('question_id', flat=True))
                for each_answer in sorted_questions:
                    try:
                        question_desc = total_yes_answers.get(question_id=each_answer['question_id'])
                        total_yes_count = question_desc['num_answers__sum']
                    except:
                        total_yes_count = 0
                    question_text = Question.objects.get(id=each_answer['question_id']).question_text
                    answers.append({'question_id': each_answer['question_id'], 'text':question_text,'percentage': "{:.2f}".format(round((total_yes_count/each_answer['num_answers__sum'])*100, 2))})
                HHSurvey["answers"] = answers
            else:
                print("No community survey data for '{}' between {} and {}".format(boundary.name, date_range))
        return HHSurvey


def get_all_boundary_HH_reports(
                                    household_survey_id,
                                    from_yearmonth, to_yearmonth):
    boundary_ids = get_boundaries_for_timeframe(
        household_survey_id, from_yearmonth, to_yearmonth)
    results = {}
    for boundary in boundary_ids:
        hh_data = getHouseholdSurvey(household_survey_id, boundary, [from_yearmonth, to_yearmonth])
        results[boundary] = hh_data
    return results

def get_HHReport_for_boundary(
                            household_survey_id, boundary_id,
                            from_yearmonth, to_yearmonth):
    results = {}
    hh_data = getHouseholdSurvey(household_survey_id, boundary_id, [from_yearmonth, to_yearmonth])
    results[boundary_id] = hh_data
    return results


def get_boundaries_for_timeframe(household_survey_id, from_yearmonth, to_yearmonth):
    """ Returns all boundaries which have household data for a given time 
    range and survey id """
    return SurveyBoundaryQuestionGroupAnsAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=household_survey_id).filter(
                    questiongroup_id__in=[18,20]).distinct(
                            'boundary_id').values_list(
                                'boundary_id', flat=True)


def get_gps_for_timeframe(
        household_survey_id,
        from_yearmonth,
        to_yearmonth):
    """ Returns a list of distinct gp_ids for the academic year 
    where household survey happened """
    return SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(
        survey_id=household_survey_id
    ).filter(
        questiongroup_id__in=[18, 20]).filter(
            yearmonth__gte=from_yearmonth).filter(
                const_ward_type='GP').filter(
                    yearmonth__lte=to_yearmonth).order_by(
                    'eboundary_id').distinct().values_list(
                    'eboundary_id', flat=True)