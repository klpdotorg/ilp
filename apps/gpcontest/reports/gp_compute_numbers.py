from assessments.models import (
    AnswerGroup_Institution,
    AnswerInstitution,
    CompetencyQuestionMap,
    QuestionGroup,
    SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    CompetencyOrder,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg
)
from schools.models import Institution
from boundary.models import (
    Boundary,
    ElectionBoundary,
    BasicElectionBoundaryAgg
)
from gpcontest.reports.utils import *
from gpcontest.models import (
    GPStudentScoreGroups,
    GPSchoolParticipationCounts
)
from django.db.models import (
    When,
    Case, Value, Sum, F, ExpressionWrapper, Count)
from django.db.models.functions import Cast
from django.db import models
import datetime
import locale

# This is to add the commas in the right places in the numbers
# SEtting it to OR because that's installed in almost all our systems
# If locale is not installed, please install first
# TODO: Should be added to our terraform, ansible config scripts

locale.setlocale(locale.LC_NUMERIC,"en_IN")

'''select assessments_answerinstitution.answergroup_id, sum(case when 
answer~'^\d+(\.\d+)?$' then case when answer::decimal>0 then answer::decimal 
end else 0 end) AS total_score, (sum(case when answer~'^\d+(\.\d+)?$' then case
when answer::decimal>0 then answer::decimal end else 0 end)/20)*100 AS percent 
from assessments_answerinstitution WHERE answergroup_id IN (select id from 
assessments_answergroup_institution where questiongroup_id IN (45,46,47) and 
institution_id IN (select id from schools_institution where gp_id=1035)) and 
assessments_answerinstitution.question_id IN (select question_id from 
assessments_competencyquestionmap where questiongroup_id=45) GROUP BY
assessments_answerinstitution.answergroup_id;'''


def get_participating_school_count(gp_id, survey_id, contest_dates):
    """Returns the number of schools that participated in a GP contest
    contest_dates: is an array of dates in the YYYYMM format when GP contests
    happened."""
    # Validate the GP ID first
    try:
        gp = ElectionBoundary.objects.get(id=gp_id)
    except:
        raise ValueError("GP %s does not exist " % gp_id)
    count_by_dates = {}
    for date in contest_dates:
        num_schools = 0
        gp_school_counts = None
        try:
            gp_school_counts = GPSchoolParticipationCounts.objects.filter(
                                            gp_id=gp_id).get(yearmonth=date)
        except:
            num_schools = 0
        if gp_school_counts is not None:
            num_schools = gp_school_counts.num_schools
        count_by_dates[date] = num_schools
    return count_by_dates
    # format_str = '%Y%m'  # The input format
    # from_datetime_obj = datetime.datetime.strptime(str(from_yearmonth), format_str)
    # to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth), format_str)

    # num_schools = AnswerGroup_Institution.objects.filter(
    #     questiongroup_id__survey_id=survey_id).filter(
    #     date_of_visit__year__gte=from_datetime_obj.year).filter(
    #         date_of_visit__year__lte=to_datetime_obj.year).filter(
    #         date_of_visit__month__gte=from_datetime_obj.month).filter(
    #         date_of_visit__month__lte=to_datetime_obj.month
    #     ).filter(institution_id__gp_id=gp_id).distinct('institution_id').count()

# def get_gradewise_score_buckets(gp_id, questiongroup_ids_list, from_date, to_date):
#     """ This method takes in a Gram Panchayat ID and a list of questiongroup
#         IDs and returns a dictionary containing child performance data
#         gradewise in score buckets of 0 - 35, 36 - 60, 61 - 75, 75 - 100 """
        
#     # Get the question ids relevant for the questiongroups and exclude
#     # two questions - Gender and CreatedBy. IDs are hardcoded below
#     selected_question_ids = AnswerInstitution.objects.filter(
#             answergroup__questiongroup__id__in=questiongroup_ids_list
#         ).exclude(question_id__in=[130, 291]).distinct(
#             'question_id').values_list(
#             'question_id', flat=True)
  
#     # Filter answers based on questiongroup and gp_id and selected questions
#     filtered_qs = AnswerInstitution.objects\
#         .filter(answergroup__date_of_visit__range=[from_date, to_date])\
#         .filter(answergroup__questiongroup__id__in=questiongroup_ids_list)\
#         .filter(answergroup__institution__gp_id=gp_id)\
#         .filter(question_id__in=selected_question_ids)\
    
#     # Calculate total scores of each child in a particular grade
#     score_aggregations = filtered_qs.values('answergroup').annotate(
#         correct_score_totals=Sum(
#             Case(
#                 When(answer__regex=r'^\d+(\.\d+)?$',
#                      then=Cast('answer', models.IntegerField())),
#                 default=0,
#                 output_field=models.IntegerField(),)))\
#         .values('answergroup__questiongroup__name', 'answergroup',
#                 'correct_score_totals')

#     # Calculate percentage scores for each child (i.e. each answergroup
#     # entry)
#     percent_scores = score_aggregations.annotate(
#         percent_score=ExpressionWrapper((F('correct_score_totals')/(
#             float(20.0)))*float(100.0), output_field=models.FloatField())
#     ).values(
#         'answergroup__questiongroup__name',
#         'answergroup',
#         'correct_score_totals',
#         'percent_score')\
#         .order_by('answergroup__questiongroup__name') 
#     # Construct return data dict
#     score_buckets = {}
#     for questiongroup_id in questiongroup_ids_list:
#         questiongroup = QuestionGroup.objects.filter(name=questiongroup_id)
#         class_scores = percent_scores.filter(
#                 answergroup__questiongroup__id=questiongroup_id)
#         # Count the number of answer groups basically. One AG=1 child
#         no_of_ag = class_scores.count()
#         below35 = class_scores.filter(percent_score__lte=35).count()
#         level2 = class_scores.filter(percent_score__gt=36).filter(
#             percent_score__lte=60).count()
#         level3 = class_scores.filter(percent_score__gt=60).filter(
#             percent_score__lte=75).count()
#         level4 = class_scores.filter(percent_score__gt=75).filter(
#             percent_score__lte=100).count()
#         score_buckets[questiongroup_id] = {
#             "total": no_of_ag,
#             "below35": below35,
#             "35to60": level2,
#             "60to75": level3,
#             "75to100": level4
#         }
#     return score_buckets

def get_gradewise_score_buckets(gp_id, questiongroup_ids_list, contest_yearmonth_dates):
    """ This method takes in a Gram Panchayat ID and a list of questiongroup
        IDs and returns a dictionary containing child performance data
        gradewise in score buckets of 0 - 35, 36 - 60, 61 - 75, 75 - 100
        The dict is keyed by qgroup id """
        
    # All the logic to compute the numbers has been moved to a materialized view
    # called mvw_survey_eboundary_answers_agg. Check the script under db_scripts
    # for details on how the computation is done
    
    # Construct return data dict
    scores_by_contest_date = {}
    for date in contest_yearmonth_dates:
        # Get the relevant rows when this particular contest happened
        score_buckets = {}
        try:
            gp_scores = GPStudentScoreGroups.objects.filter(
                        gp_id=gp_id).filter(
                            yearmonth=date)
        except:
            pass
        else:
            for questiongroup_id in questiongroup_ids_list:
                questiongroup = QuestionGroup.objects.get(id=questiongroup_id)
                # if questiongroup.name not in score_buckets:
                score_buckets[questiongroup_id] = {}
                try:
                    grade_scores = gp_scores.get(questiongroup_id=questiongroup_id)
                except:
                    grade_scores = None
                #print("No questiongroup %s for GP %s:" % (questiongroup_id, gp_id))
                if grade_scores is not None:
                    score_buckets[questiongroup_id] = {
                        "total": grade_scores.num_students,
                        "below35": grade_scores.cat_a,
                        "35to59": grade_scores.cat_b,
                        "60to74": grade_scores.cat_c,
                        "75to100": grade_scores.cat_d
                    }
                else:
                    score_buckets[questiongroup_id] = {
                        "total": 0,
                    }
            scores_by_contest_date[date] = score_buckets
    return scores_by_contest_date

def get_gradewise_competency_correctscores(gp_id, gpcontest_survey_id,
                                           report_from, report_to):
    """
        Computes the number of students in EACH GRADE in the GP who answered
        correctly for the competencies in the given time frame, survey_id and
        the Gram Panchayat id. Returns a queryset which can be further
        filtered or manipulated
    """
    correct_answers_agg = []
    try:
        correct_answers_agg = \
            SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
            .filter(survey_id=gpcontest_survey_id,
                    eboundary_id=gp_id, survey_tag='gka')\
            .filter(yearmonth__gte=report_from)\
            .filter(yearmonth__lte=report_to)\
            .values('question_key', 'questiongroup_name',
                    'questiongroup_id')\
            .annotate(correct_answers=Sum('num_assessments'))
    except SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
        pass
    return correct_answers_agg


def get_grade_competency_correctscores(gp_id, qgroup_id, gpcontest_survey_id,
                                            report_from, report_to):
    """
        Computes the number of students in a given grade
        who answered correctly for all competencies in the given time frame,
        survey_id and the Gram Panchayat id. Returns a queryset which can be
        further filtered or manipulated
    """
    correct_answers_agg = None
    try:
        correct_answers_agg = \
            SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
            .filter(survey_id=gpcontest_survey_id,
                    eboundary_id=gp_id, survey_tag='gka')\
            .filter(questiongroup_id=qgroup_id)\
            .filter(yearmonth__gte=report_from)\
            .filter(yearmonth__lte=report_to)\
            .values('question_key')\
            .annotate(correct_answers=Sum('num_assessments'))
    except SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
        pass
    return correct_answers_agg

def get_total_assessments_for_grade(gp_id, qgroup_id, gpcontest_survey_id,
                                  report_from, report_to):
    total_assessments = None
    try:
        total_assessments = SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects\
                .filter(survey_id=gpcontest_survey_id,
                        eboundary_id=gp_id, survey_tag='gka')\
                .filter(questiongroup_id=qgroup_id)\
                .filter(yearmonth__gte=report_from)\
                .filter(yearmonth__lte=report_to)\
                .values('question_key', 'yearmonth')\
                .annotate(total_answers=Sum('num_assessments'))
    except SurveyEBoundaryQuestionGroupQuestionKeyAgg.DoesNotExist:
        pass
    return total_assessments

def get_schoolcount_classes_gplist(
        survey_id, gp_list, from_yearmonth, to_yearmonth):
    """ Return number of schools with class 4 assessments, 5 assessments, 6
    assessments """
    qgroup_names = get_questiongroup_names_survey(
                        survey_id, from_yearmonth, to_yearmonth)
    queryset = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id__gp_id__in=gp_list).filter(yearmonth__gte=from_yearmonth).filter(
                yearmonth__lte=to_yearmonth).values('questiongroup_id','yearmonth')
    result = {}
    for qgroup_name in qgroup_names:
        ids = QuestionGroup.objects.filter(name=qgroup_name)
        result[qgroup_name] = {}
        for id in ids:
            num_schools = queryset.filter(questiongroup_name=qgroup_name).distinct('institution_id').count()
            result[qgroup_name][id] = num_schools
    return result

def get_schoolcount_classes_count(
        survey_id, gp_id, from_yearmonth, to_yearmonth, contest_dates_yearmonth):
    """ Return number of schools with class 4 assessments, 5 assessments, 6
    assessments """
    qgroup_names = get_questiongroup_names_survey(
                        survey_id, from_yearmonth, to_yearmonth)
    queryset = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id__gp_id=gp_id).filter(yearmonth__gte=from_yearmonth).filter(
                yearmonth__lte=to_yearmonth)
    result = {}
    for date in contest_dates_yearmonth:
        qgroups_count_by_date = {}
        for qgroup_name in qgroup_names: 
            num_schools = queryset.filter(
                                    questiongroup_name=qgroup_name).values(
                                        'yearmonth', 'institution_id').distinct().count()
            qgroups_count_by_date[qgroup_name] = num_schools
        result[date] = qgroups_count_by_date
    return result


def get_grade_competency_percentages(gp_id, qgroup_id, gpcontest_survey_id,
                                     report_from, report_to, contest_dates):
    """
        Computes the percentage of students who are fluent in a competency
        in the given time frame, survey_id and the Gram Panchayat
        id. Returns a queryset which can be further filtered or manipulated
    """
    correct_answers_agg = get_grade_competency_correctscores(
                                gp_id, qgroup_id,
                                gpcontest_survey_id, report_from,
                                report_to)
    
    total_assessments = get_total_assessments_for_grade(gp_id, qgroup_id,
                                                        gpcontest_survey_id,
                                                        report_from,
                                                        report_to)
    results_by_date = {}
    if total_assessments is not None and correct_answers_agg is not None:
        for contest_date in contest_dates:
            
            competency_order = CompetencyOrder.objects.filter(questiongroup=qgroup_id).order_by('sequence').values_list('key', flat=True)
            list_of_competencies = ["Number Recognition", "Place Value",
                "Addition", "Subtraction", "Multiplication", "Division"]
            # Find which competencies are not there in the DB and make them NA
            # to make it easier for LaTex templates to process because LaTex
            # has hardcoding of competencies and code needs to return NA for
            # those which are not there in DB
            diff_list = list(set(list_of_competencies) - set(competency_order))
            
            # These are all the competencies LaTex expects
            concept_scores = {
                "Number Recognition": 0,
                "Place Value": 'NA',
                "Addition": 0,
                "Subtraction": 0,
                "Multiplication": 0,
                "Division": 0
            }
            for item in diff_list:  # These are the competencies NA
                concept_scores[item] = 'NA'
            correct_ans_for_date = correct_answers_agg.filter(yearmonth=contest_date)
            total_ans_for_date = total_assessments.filter(yearmonth=contest_date)
            for each_row in total_ans_for_date:
                current_question_key = each_row['question_key']
                sum_total = each_row['total_answers']
                try:
                    sum_correct_ans = correct_ans_for_date.get(
                        question_key=current_question_key)['correct_answers']
                except:
                    sum_correct_ans = None
                if sum_correct_ans is None:
                    sum_correct_ans = 0
                percentage = 0
                if sum_total is not None:
                    percentage = round((sum_correct_ans / sum_total)*100, 2)
                else:
                    percentage = 0
                concept_scores[current_question_key] = percentage
            results_by_date[contest_date] = concept_scores
    return results_by_date


def getCompetencyPercPerSchool(survey_id, school_id, key, from_yearmonth, to_yearmonth):
    """ For household reports, that need addition/subtraction percentages
        per school """
    total_ans = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id=school_id).filter(yearmonth__gte=from_yearmonth).filter(
                yearmonth__lte=to_yearmonth).filter(
                    question_key=key).values('survey_id', 'institution_id', 'question_key').annotate(total_answers=Sum('num_assessments'))
    total = None
    if total_ans:
        total_ans=total_ans[0]
    if total_ans and total_ans["total_answers"] is not None:
        total = total_ans['total_answers']
    correct_ans = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id=school_id).filter(yearmonth__gte=from_yearmonth).filter(
                yearmonth__lte=to_yearmonth).filter(
                    question_key=key).values('survey_id', 'institution_id', 'question_key').annotate(total_answers=Sum('num_assessments'))
    correct = 0
    if correct_ans:
        correct_answer=correct_ans[0]
    if correct_ans and correct_answer['total_answers'] is not None:
        correct = correct_answer['total_answers']
    if total is None:
        # Data unavailable for this GP for this competency
        perc='NA'
    elif total > 0:
        perc = round((correct / total) * 100, 2)
    else:
        perc = 0
    return perc
