from assessments.models import (
    AnswerGroup_Institution,
    AnswerInstitution,
    CompetencyQuestionMap,
    QuestionGroup,
    SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg
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


def get_participating_school_count(gp_id, survey_id, from_yearmonth, to_yearmonth):
    """Returns the number of schools that participated in a GP contest"""
    # Validate the GP ID first
    try:
        gp = ElectionBoundary.objects.get(id=gp_id)
    except:
        raise ValueError("GP %s does not exist " % gp_id)
    num_schools = 0
    gp_school_counts = None
    try:
        gp_school_counts = GPSchoolParticipationCounts.objects.get(gp_id=gp_id)
    except:
        num_schools = 0
    if gp_school_counts is not None:
        num_schools = gp_school_counts.num_schools
    return num_schools
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

def get_gradewise_score_buckets(gp_id, questiongroup_ids_list, from_yearmonth, to_yearmonth):
    """ This method takes in a Gram Panchayat ID and a list of questiongroup
        IDs and returns a dictionary containing child performance data
        gradewise in score buckets of 0 - 35, 36 - 60, 61 - 75, 75 - 100 """
        
    # All the logic to compute the numbers has been moved to a materialized view
    # called mvw_survey_eboundary_answers_agg. Check the script under db_scripts
    # for details on how the computation is done
    
    # Construct return data dict
    score_buckets = {}
    try:
        gp_scores = GPStudentScoreGroups.objects.filter(gp_id=gp_id)
    except:
        pass
    else:
        for questiongroup_id in questiongroup_ids_list:
            questiongroup = QuestionGroup.objects.get(id=questiongroup_id)
            if questiongroup.name not in score_buckets:
                score_buckets[questiongroup.name] = {}
            try:
                grade_scores = gp_scores.get(questiongroup_id=questiongroup_id)
            except:
                grade_scores = None
            #print("No questiongroup %s for GP %s:" % (questiongroup_id, gp_id))
            if grade_scores is not None:
                score_buckets[questiongroup.name] = {
                    "total": grade_scores.num_students,
                    "below35": grade_scores.cat_a,
                    "35to60": grade_scores.cat_b,
                    "60to75": grade_scores.cat_c,
                    "75to100": grade_scores.cat_d
                }
            else:
                score_buckets[questiongroup.name] = {
                    "total": 0,
                }
    return score_buckets


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
                .values('question_key')\
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
                yearmonth__lte=to_yearmonth)
    result = {}
    for qgroup_name in qgroup_names:
        num_schools = queryset.filter(questiongroup_name=qgroup_name).distinct('institution_id').count()
        result[qgroup_name] = num_schools
    return result

def get_schoolcount_classes_count(
        survey_id, gp_id, from_yearmonth, to_yearmonth):
    """ Return number of schools with class 4 assessments, 5 assessments, 6
    assessments """
    qgroup_names = get_questiongroup_names_survey(
                        survey_id, from_yearmonth, to_yearmonth)
    queryset = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=survey_id).filter(
            institution_id__gp_id=gp_id).filter(yearmonth__gte=from_yearmonth).filter(
                yearmonth__lte=to_yearmonth)
    result = {}
    for qgroup_name in qgroup_names:
        num_schools = queryset.filter(questiongroup_name=qgroup_name).distinct('institution_id').count()
        result[qgroup_name] = num_schools
    return result


def get_grade_competency_percentages(gp_id, qgroup_id, gpcontest_survey_id,
                                     report_from, report_to):
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
    concept_scores = {}
    if total_assessments is not None and correct_answers_agg is not None:
        for each_row in total_assessments:
            current_question_key = each_row['question_key']
            sum_total = each_row['total_answers']
            try:
                sum_correct_ans = correct_answers_agg.get(
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
    return concept_scores
