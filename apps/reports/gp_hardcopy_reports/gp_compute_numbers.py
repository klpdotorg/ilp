from assessments.models import (
    AnswerGroup_Institution,
    AnswerInstitution,
    CompetencyQuestionMap,
    QuestionGroup,
    SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg
)
from schools.models import Institution
from boundary.models import (
    Boundary,
    ElectionBoundary,
    BasicElectionBoundaryAgg
)
from django.db.models import (
    When,
    Case, Value, Sum, F, ExpressionWrapper, Count)
from django.db.models.functions import Cast
from django.db import models

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


def get_general_gp_info(gp_id, acadyear):
    """Returns general GP info for an academic year"""
    # Validate the GP ID first
    try:
        gp = ElectionBoundary.objects.get(id=gp_id)
    except:
        raise ValueError("GP %s does not exist " % gp_id)
    
    schools_in_gp = Institution.objects.filter(gp_id=gp_id) 
    if schools_in_gp is not None and schools_in_gp.count() > 0:
        cluster_id = schools_in_gp.first().admin3_id
        block_id = schools_in_gp.first().admin2_id
        district_id = schools_in_gp.first().admin1_id
    try:
        gp_name = gp.const_ward_name
        eboundary = BasicElectionBoundaryAgg.objects.filter(
            electionboundary_id=gp_id).get(
                year=acadyear
            )
    except:
        raise ValueError(
            "GP info for academic year %s and GP id %s does not exist " % (acadyear,gp_id))
    else:
        cluster_name = Boundary.objects.get(id=cluster_id).name
        block_name = Boundary.objects.get(id=block_id).name
        district_name = Boundary.objects.get(id=district_id).name
        if eboundary is not None:
            num_students = eboundary.num_students
            num_schools = eboundary.num_schools
        else:
            num_students = 0
            num_schools = 0
        gp_info = {
            "name": gp_name,
            "block": block_name,
            "district": district_name,
            "cluster": cluster_name,
            "school_count": num_schools
        }
        return gp_info


def get_gradewise_score_buckets(gp_id, questiongroup_ids_list, from_date, to_date):
    """ This method takes in a Gram Panchayat ID and a list of questiongroup
        IDs and returns a dictionary containing child performance data
        gradewise in score buckets of 0 - 35, 36 - 60, 61 - 75, 75 - 100 """
        
    # Get the question ids relevant for the questiongroups and exclude
    # two questions - Gender and CreatedBy. IDs are hardcoded below
    selected_question_ids = AnswerInstitution.objects.filter(
            answergroup__questiongroup__id__in=questiongroup_ids_list
        ).exclude(question_id__in=[130, 291]).distinct(
            'question_id').values_list(
            'question_id', flat=True)
  
    # Filter answers based on questiongroup and gp_id and selected questions
    filtered_qs = AnswerInstitution.objects\
        .filter(answergroup__date_of_visit__range=[from_date, to_date])\
        .filter(answergroup__questiongroup__id__in=questiongroup_ids_list)\
        .filter(answergroup__institution__gp_id=gp_id)\
        .filter(question_id__in=selected_question_ids)\
    
    # Calculate total scores of each child in a particular grade
    score_aggregations = filtered_qs.values('answergroup').annotate(
        correct_score_totals=Sum(
            Case(
                When(answer__regex=r'^\d+(\.\d+)?$',
                     then=Cast('answer', models.IntegerField())),
                default=0,
                output_field=models.IntegerField(),)))\
        .values('answergroup__questiongroup__name', 'answergroup',
                'correct_score_totals')

    # Calculate percentage scores for each child (i.e. each answergroup
    # entry)
    percent_scores = score_aggregations.annotate(
        percent_score=ExpressionWrapper((F('correct_score_totals')/(
            float(20.0)))*float(100.0), output_field=models.FloatField())
    ).values(
        'answergroup__questiongroup__name',
        'answergroup',
        'correct_score_totals',
        'percent_score')\
        .order_by('answergroup__questiongroup__name') 
    # Construct return data dict
    score_buckets = {}
    for questiongroup_id in questiongroup_ids_list:
        questiongroup = QuestionGroup.objects.filter(name=questiongroup_id)
        class_scores = percent_scores.filter(
                answergroup__questiongroup__id=questiongroup_id)
        # Count the number of answer groups basically. One AG=1 child
        no_of_ag = class_scores.count()
        below35 = class_scores.filter(percent_score__lte=35).count()
        level2 = class_scores.filter(percent_score__gt=36).filter(
            percent_score__lte=60).count()
        level3 = class_scores.filter(percent_score__gt=60).filter(
            percent_score__lte=75).count()
        level4 = class_scores.filter(percent_score__gt=75).filter(
            percent_score__lte=100).count()
        score_buckets[questiongroup_id] = {
            "total": no_of_ag,
            "below35": below35,
            "35to60": level2,
            "60to75": level3,
            "75to100": level4
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
    correct_answers_agg = []
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
                percentage = (sum_correct_ans / sum_total)*100
            else:
                percentage = 0
            concept_scores[current_question_key] = percentage
    return concept_scores