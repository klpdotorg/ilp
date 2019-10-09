from assessments.models import (
    SurveyEBoundaryQuestionGroupAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyInstitutionRespondentTypeAgg,
    SurveyInstitutionQuestionGroupAnsAgg,
    Question,
    QuestionGroup_Questions
    )
from gpcontest.models import (
    SurveyInstitutionHHRespondentTypeAnsAgg,
    HHSurveyInstitutionQuestionAnsAgg
)
from gpcontest.reports.gp_compute_numbers import (
    getCompetencyPercPerSchool
)
from schools.models import Institution
from boundary.models import (
    Boundary, ElectionBoundary
)
from django.db.models import Sum, F, Count


def getParentalPerception(survey_id, school_id, date_range):
    question_ids = [149, 150, 138]
    perception_qs = SurveyInstitutionHHRespondentTypeAnsAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id=school_id).filter(
            yearmonth__range=date_range).filter(
                question_id__in=question_ids).filter(respondent_type='Parents').order_by('question_id').values(
                    'question_id', 'question_desc', 'num_yes', 'num_no', 'num_unknown')
    result = {}
    for perception in perception_qs:
        total = perception["num_yes"] + perception["num_no"] + perception["num_unknown"]
        if perception["question_id"] == 149:
            result["Addition"] = round(perception["num_yes"]*100/total)
        elif perception["question_id"] == 150:
            result["Subtraction"] = round(perception["num_yes"]*100/total)
        elif perception["question_id"] == 138:
            result["Separate Toilets"] = round(perception["num_yes"]*100/total)
    return result


def getGPContestPercentages(gp_survey_id, school_id, date_range):
    addition_perc = getCompetencyPercPerSchool(
        gp_survey_id, school_id, 'Addition', date_range[0], date_range[1])
    subtraction_perc = getCompetencyPercPerSchool(
        gp_survey_id, school_id, 'Subtraction', date_range[0], date_range[1])
    return {
        "Addition": addition_perc,
        "Subtraction": subtraction_perc
    }

def getHouseholdSurveyForSchool(survey_id, gp_survey_id, school_id, date_range):
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
                hh_answers_agg = HHSurveyInstitutionQuestionAnsAgg.objects.filter(institution_id=school_id)
            except HHSurveyInstitutionQuestionAnsAgg.DoesNotExist:
                print("No community survey data for '{}' between {} and {}".format(school_id, date_range))
                raise ValueError("No community survey data for '{}' between {} and {}".format(school_id, date_range))
            # Find the total number of assessments
            total_assess = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id=school_id) \
                .filter(
                    yearmonth__range=date_range, questiongroup_id__in=[18, 20]
                    ).filter(survey_tag='konnect').values(
                        'survey_id', 'institution_id'
                    ).annotate(total=Sum('num_assessments'))
            HHSurvey['total_assessments'] = total_assess[0]['total']
            # Find the total number of parental assessments
            total_parental_assess = SurveyInstitutionRespondentTypeAgg.objects. \
                filter(institution_id=school_id) \
                .filter(
                    yearmonth__range=date_range, survey_id=7
                    ).filter(survey_tag='konnect').values(
                        'survey_id', 'institution_id'
                    ).annotate(total=Sum('num_assessments'))
            HHSurvey['total_parental_assessments'] = total_parental_assess[0]['total']

            #Run through the questions
            if hh_answers_agg is not None and hh_answers_agg.exists():
                HHSurvey['school_name'] = school.name
                HHSurvey['district_name'] = school.admin1.name
                HHSurvey['block_name'] = school.admin2.name
                HHSurvey['cluster_name'] = school.admin3.name

                if school.gp is not None:
                    HHSurvey['gp_name'] = school.gp.const_ward_name
                    HHSurvey['gp_id'] = school.gp.id 
                else:
                    HHSurvey['gp_name'] = "Unknown"
                    HHSurvey['gp_id'] = "Unknown"
                if school.village is not None:
                    HHSurvey['village_name'] = school.village
                else:
                    HHSurvey['village_name'] = "Unknown"
                if school.dise is not None and school.dise.school_code is not None:
                    HHSurvey['dise_code'] = school.dise.school_code
                else:
                    HHSurvey['dise_code'] = 'Unknown'
                HHSurvey['parents_perception'] = getParentalPerception(survey_id, school_id, date_range)
                HHSurvey['gpcontest_data'] = getGPContestPercentages(gp_survey_id, school_id, date_range)
                sorted_questions = hh_answers_agg.order_by('order')
                for each_answer in sorted_questions:
                    answers.append({
                        'question_id': each_answer.question_id.id,
                        'text': each_answer.question_desc,
                        'lang_text': each_answer.lang_questiondesc,
                        'percentage_yes': each_answer.perc_yes,
                        'percentage_no': each_answer.perc_no,
                        'percentage_unknown': each_answer.perc_unknown
                       })
                HHSurvey["answers"] = answers
            else:
                print("No community survey data for '{}' between {} and {}".format(school.name, date_range))
        return HHSurvey


# def getHouseholdSurveyForBoundary(survey_id,boundary_id,date_range):
#         """ Returns household survey aggregate values in a dictionary per boundary """
#         boundary = None
#         # Boundary has to be a Boundary or ElectionBoundary
#         try:
#             boundary = Boundary.objects.get(id=boundary_id)
#         except:
#             boundary = ElectionBoundary.objects.get(id=boundary_id)
#         hh_answers_agg = None
#         HHSurvey = {}
#         answers = []
#         boundary_type = None
#         if boundary is not None:
#             boundary_type = ""
#             boundary_name = ""
#             if isinstance(boundary, ElectionBoundary):
#                 boundary_type = boundary.const_ward_type_id
#                 boundary_name = boundary.const_ward_name
#                 try:
#                     hh_answers_agg = SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(eboundary_id=boundary)\
#                         .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])
#                 except SurveyEBoundaryQuestionGroupAnsAgg.DoesNotExist:
#                     print("No community survey data for '{}' between {} and {}".format(boundary.const_ward_name, date_range))
#             else:
#                 #Household Survey
#                 boundary_type = boundary.boundary_type_id
#                 boundary_name = boundary.name
#                 hh_answers_agg = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=boundary)\
#                     .filter(yearmonth__range=date_range,questiongroup_id__in=[18,20])
#             if hh_answers_agg is not None and hh_answers_agg.exists():
#                 HHSurvey['boundary_name'] = boundary_name
#                 HHSurvey['boundary_type'] = boundary_type
#                 total_hh_answers = hh_answers_agg.values('question_id').annotate(Sum('num_answers'))
#                 total_yes_answers = hh_answers_agg.filter(answer_option='Yes').values('question_id').annotate(Sum('num_answers'))
#                 total_no_answers = hh_answers_agg.filter(answer_option='No').values('question_id').annotate(Sum('num_answers'))
#                 total_unknown_answers = hh_answers_agg.filter(answer_option='Don\'t Know').values('question_id').annotate(Sum('num_answers'))
#                 ordered_list = QuestionGroup_Questions.objects.filter(questiongroup_id__in=[18, 20]).order_by('sequence', 'question_id').distinct('sequence', 'question_id').values_list('question_id', flat=True)
#                 ordered_list = list(ordered_list)
#                 sorted_questions = sorted(total_hh_answers, key=lambda q: ordered_list.index(q['question_id']))
#                 #print(sorted_questions.values_list('question_id', flat=True))
#                 for each_answer in sorted_questions:
#                     try:
#                         question_desc = total_yes_answers.get(question_id=each_answer['question_id'])
#                         total_yes_count = question_desc['num_answers__sum']
#                     except:
#                         total_yes_count = 0
#                     question_text = Question.objects.get(id=each_answer['question_id']).question_text
#                     answers.append({'question_id': each_answer['question_id'], 'text':question_text,'percentage': "{:.2f}".format(round((total_yes_count/each_answer['num_answers__sum'])*100, 2))})
#                 HHSurvey["answers"] = answers
#             else:
#                 print("No community survey data for '{}' between {} and {}".format(boundary.name, date_range))
#         return HHSurvey


"""
Generates household reports for all schools in all applicable boundaries
for a given academic year
"""


def get_all_hh_reports(
                        household_survey_id,gpc_survey_id,
                        from_yearmonth, to_yearmonth):
    school_ids = get_schools_for_timeframes(
        household_survey_id, from_yearmonth, to_yearmonth)
    results = {}
    for school in school_ids:
        hh_data = ggetHouseholdSurveyForSchool(household_survey_id, gpc_survey_id,school, [from_yearmonth, to_yearmonth])
        results[school] = hh_data
    return results


def get_hh_reports_for_districts(
                                    household_survey_id, gpc_survey_id,
                                    boundary_ids, from_yearmonth,
                                    to_yearmonth):
    """
    Returns the household report for a given list of boundary IDs
    """
    school_ids = get_schools_for_districts(
        household_survey_id, boundary_ids, from_yearmonth, to_yearmonth)
    results = {}
    for school in school_ids:
        hh_data = getHouseholdSurveyForSchool(household_survey_id, gpc_survey_id, school, [from_yearmonth, to_yearmonth])
        results[school] = hh_data
    return results

def get_hh_reports_for_gps(
                            household_survey_id, gpc_survey_id,
                            gp_ids, from_yearmonth,
                            to_yearmonth):
    school_ids = get_schools_for_gps(household_survey_id, gp_ids, from_yearmonth, to_yearmonth)
    results = {}
    for school in school_ids:
        hh_data = getHouseholdSurveyForSchool(household_survey_id, gpc_survey_id, school, [from_yearmonth, to_yearmonth])
        results[school] = hh_data
    return results

    
def get_hh_reports_for_school_ids(
                                    household_survey_id, gpc_survey_id,school_ids,
                                    from_yearmonth, to_yearmonth):
    results = {}
    for school in school_ids:
        hh_data = getHouseholdSurveyForSchool(household_survey_id, gpc_survey_id,school, [from_yearmonth, to_yearmonth])
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

def get_schools_for_gps(household_survey_id, gp_list, from_yearmonth, to_yearmonth):
    return SurveyInstitutionQuestionGroupAnsAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=household_survey_id).filter(
                    questiongroup_id__in=[18, 20]).filter(
                        institution_id__gp__in=gp_list).distinct(
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