from assessments.models import (
    SurveyEBoundaryQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    SurveyInstitutionQuestionGroupAnsAgg
    Question,
    QuestionGroup_Questions
    )
from schools.models import Institution
from boundary.models import (
    Boundary, ElectionBoundary
)
from django.db.models import Sum

def getHouseholdSurveyForSchool(survey_id,school_id,date_range):
        """ Returns household survey aggregate values in a dictionary per boundary """
        school = None
        try:
           school = Institution.objects.get(id=school_id)
        except:
            print("No such school ID")
            raise ValueError("No school ID %s" % school_id)
        hh_answers_agg = None
        HHSurvey = {}
        answers = []
        if school is not None:
            try:
                hh_answers_agg = SurveyInstitutionQuestionGroupAnsAgg.objects.filter(institution_id=boundary)\
                    .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])
            except SurveyInstitutionQuestionGroupAnsAgg.DoesNotExist:
                print("No community survey data for '{}' between {} and {}".format(school, date_range))
           
            if hh_answers_agg is not None and hh_answers_agg.exists():
                HHSurvey['school_name'] = school.name
                HHSurvey['district_name'] = school.admin1.name
                HHSurvey['block_name'] = school.admin2.name
                HHSurvey['cluster_name'] = school.admin3.name
                HHSurvey['gp_name'] = school.gp.const_ward_name
                HHSurvey['gp_id'] = school.gp.id
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


def getHouseholdSurveyForBoundary(survey_id,boundary_id,date_range):
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


"""
Generates household reports for all schools in all applicable boundaries
for a given academic year
"""


def getAllSchoolHHReports(
                            household_survey_id,
                            from_yearmonth, to_yearmonth):
    school_ids = get_schools_for_timeframes(
        household_survey_id, from_yearmonth, to_yearmonth)
    results = {}
    for school in school_ids:
        hh_data = ggetHouseholdSurveyForSchool(household_survey_id, school, [from_yearmonth, to_yearmonth])
        results[school] = hh_data
    return results


def getSchoolHHReportsForDistricts(
                                    household_survey_id,
                                    boundary_ids, from_yearmonth,
                                    to_yearmonth):
    """
    Returns the household report for a given list of boundary IDs
    """
    school_ids = get_schools_for_districts(
        household_survey_id, boundary_ids, from_yearmonth, to_yearmonth)
    results = {}
    for school in school_ids:
        hh_data = ggetHouseholdSurveyForSchool(household_survey_id, school, [from_yearmonth, to_yearmonth])
        results[school] = hh_data
    return results


def generate_HHReport_for_boundaries(
                            household_survey_id, boundary_ids,
                            from_yearmonth, to_yearmonth):
    results = {}
    for boundary in boundary_ids:
        hh_data = getHouseholdSurveyForBoundary(household_survey_id, boundary, [from_yearmonth, to_yearmonth])
        results[boundary] = hh_data
    return results


def get_schools_for_districts(household_survey_id, district_list, from_yearmonth,
                              to_yearmonth):
    """ Get schools for a given district """
    return SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=household_survey_id).filter(
                    questiongroup_id__in=[18, 20]).filter(
                        institution_id__admin1__in=district_list).distinct(
                            'institution_id').values_list(
                                'institution_id', flat=True)

def get_schools_for_timeframe(household_survey_id, from_yearmonth, to_yearmonth):
    """ Returns all schools which have household data for a given time 
    range and survey id """
    return SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=household_survey_id).filter(
                    questiongroup_id__in=[18,20]).distinct(
                            'institution_id').values_list(
                                'institution_id', flat=True)

def get_schools_for_districts(household_survey_id, boundary_list, from_yearmonth, to_yearmonth):
    """ Returns all schools which have household data for a given time 
    range and survey id """
    return SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=household_survey_id).filter(
                    questiongroup_id__in=[18,20]).distinct(
                            'institution_id').values_list(
                                'institution_id', flat=True)
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