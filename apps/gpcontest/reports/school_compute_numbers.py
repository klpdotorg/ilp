from assessments.models import (
    SurveyInstitutionQuestionGroupQDetailsAgg,
    SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg,
    QuestionGroup,
    QuestionGroup_Questions,
    AnswerGroup_Institution
)
from schools.models import (
    Institution
)
from gpcontest.models import (
    GPInstitutionClassParticipationCounts,
    GPInstitutionClassQDetailsAgg
)
from django.db.models import (
    When,
    Case, Value, Sum, F, ExpressionWrapper, Count)
from django.db.models.functions import Cast
from django.db import models
from .utils import *
from heapq import nsmallest
import time

def compute_deficient_competencies(school_id, questiongroup_id, survey_id,
                                   from_yearmonth, to_yearmonth):
    """
        Return a dictionary with the questiongroup_name and
        array of 3 question keys (competencies) less than 60%
        that the class is most deficient in. The return dict is of the format:
        {
            "Class 4 Assessment": ['Addition', 'Subtraction', 'Multiplication'],
            Questiongroup2_Name: [xx,yy,xx],
            .....
        }
    """
    dates = [from_yearmonth, to_yearmonth]
    correct_answers_agg =\
        SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(
            survey_id=survey_id).filter(
                questiongroup_id=questiongroup_id).filter(
                institution_id=school_id, yearmonth__range=dates).values(
                'question_key', 'lang_question_key', 'questiongroup_name',
                'num_assessments').annotate(total=Sum('num_assessments'))
    total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects\
        .filter(survey_id=survey_id, questiongroup_id=questiongroup_id,
                institution_id=school_id, yearmonth__range=dates)\
        .values('question_key', 'lang_question_key', 'questiongroup_name',
                'num_assessments')\
        .annotate(Sum('num_assessments'))
    competency_map = {}
    for each_row in total_assessments:
        sum_total = each_row['num_assessments__sum']
        percent = 0
        total = 0
        total_correct_answers = 0
        try:
            sum_correct_ans = correct_answers_agg.filter(
                question_key=each_row['question_key'])
            if sum_total is not None:
                total = sum_total
            if sum_correct_ans is None or sum_correct_ans['total'] is None:
                total_correct_answers = 0
            else:
                total_correct_answers = sum_correct_ans['total']
        except Exception as e:
            pass

        if total is not None and total > 0:
            percent = round(total_correct_answers / total * 100, 2)
        # We are only interested in competencies below 60% to call them
        # deficient. Ignore percentages above 60
        if percent < 60.00:
            competency_map[each_row['lang_question_key']] = percent
    three_smallest = nsmallest(3, competency_map, key=competency_map.get)
    return three_smallest


def get_date_of_contest(school_id, gp_survey_id, from_yearmonth, to_yearmonth):
    from_date, to_date = convert_yearmonth_to_fulldate(from_yearmonth, to_yearmonth)
    dates_of_contest = AnswerGroup_Institution.objects.filter(
        institution_id=school_id).filter(
        questiongroup__survey_id=gp_survey_id).filter(
            date_of_visit__range=[from_date, to_date]
        ).distinct('date_of_visit').values_list('date_of_visit', flat=True)
    # Format the datetime objects into a readable string and return
    formatted_dates = []
    for date in dates_of_contest:
        formatted_dates.append(date.strftime('%d/%m/%Y'))
    return formatted_dates


def get_school_report_dict(school_id, survey_id, from_yearmonth, to_yearmonth):
    """ This is the same as get_school_report except it returns a dict
    with a SINGLE school report keyed by school id"""
    result = {}
    school_report = get_school_report(
                                    school_id, survey_id,
                                    from_yearmonth, to_yearmonth)
    result[school_id] = school_report
    return result


def get_school_report(school_id, survey_id, from_yearmonth, to_yearmonth):
    """
    Internal function that returns a single school report as a dict
    TODO: Make this private
    """
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(
        str(from_yearmonth), format_str)
    to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth), format_str)

    date_of_contest = get_date_of_contest(
        school_id, survey_id, from_yearmonth, to_yearmonth)
  
    # Get questiongroups applicable for this survey ID for the given year range
    questiongroup_ids = get_questiongroups_survey(
        survey_id,
        from_yearmonth,
        to_yearmonth)
    result = {}

    school_info = Institution.objects.get(id=school_id)
    queryset = GPInstitutionClassQDetailsAgg.objects.filter(
        institution_id=school_info.id)

    result["school_id"] = school_info.id
    result["school_name"] = school_info.name
    if school_info.dise is not None:
        result["dise_code"] = school_info.dise.school_code
    result["district_name"] = school_info.admin1.name
    result["block_name"] = school_info.admin2.name
    result["cluster_name"] = school_info.admin3.name
    result["gp_id"] = school_info.gp.id
    result["gp_name"] = school_info.gp.const_ward_name
    result["date"] = date_of_contest
    for each_class in questiongroup_ids:
        try:
            class_participation =\
                GPInstitutionClassParticipationCounts.objects.filter(
                    institution_id=school_id).get(
                        questiongroup_id=each_class)
        except GPInstitutionClassParticipationCounts.DoesNotExist:
            print("This GP does not have class %s" % each_class)
        else:
            if class_participation is not None:
                num_students = class_participation.num_students
            # Find the lowest 3 competencies below 60% for each class of this
            # school
            deficiencies = compute_deficient_competencies(
                            school_id, each_class, survey_id,
                            from_yearmonth, to_yearmonth)
            class_answers = queryset.filter(
                questiongroup_id=each_class).order_by('question_sequence')
            class_details = {"num_students": num_students}
            class_questions = []
            if class_answers is not None:
                # for answer in correct_answers_for_class:
                for answer in class_answers:
                    question_answer_details = {}
                    question_answer_details["question"] =\
                        answer.microconcept.char_id
                    question_answer_details["lang_name"] = \
                        answer.question_local_lang_text
                    question_answer_details["num_correct"] = \
                        float(answer.correct_answers)
                    question_answer_details["percent"] = \
                        float(answer.percent_score)
                    class_questions.append(question_answer_details)
                class_details["question_answers"] = class_questions
                qgroup = QuestionGroup.objects.get(id=each_class)
                # Check if a class exists because sometimes it might not for
                # a particular school
                if deficiencies is not None:
                    class_details["deficiencies"] = deficiencies
                result[qgroup.name] = class_details
    return result


def get_gp_schools_report(gp_id, survey_id, from_yearmonth, to_yearmonth):
    """ From and to date is of the format YYYYMM. Return dictionary with all
    schools data for a GP. Dict format is:
    {
        school_id: {
                    'school_id': xxxx,
                    'school_name': xxxx,
                    'dise_code': xxxx,
                    'district_name': xxxx,
                    'block_name': xxxxx,
                    'cluster_name': xxxx,
                    'gp_name': xxxxx,
                    'num_students': xxx,
                    questiongroup1_name:{
                        'question_answers': [
                            {
                            'question': 'subtraction_without_borrow(abstract)', 
                            'lang_name': None, 
                            'num_correct': 0, 
                            'percent': 0.0}
                            }, 
                            {question2},
                            ..........,
                            ..........
                        ],
                        'deficiencies': {
                            ['Competency1', 'Competency2', 'Competency3']
                        }
                    },
                    questiongroup2_name: {
                        ..............
                    }
    }
    """
    start = time.time()
    total_answers = SurveyInstitutionQuestionGroupQDetailsAgg.objects.filter(
        survey_id=survey_id,
        yearmonth__gte=from_yearmonth,
        yearmonth__lte=to_yearmonth).filter(
            institution_id__gp_id=gp_id
    )
    # Get questiongroups applicable for this survey ID for the given year range
    questiongroup_ids = get_questiongroups_survey(
        survey_id,
        from_yearmonth,
        to_yearmonth)
    schools = total_answers.filter(
        questiongroup_id__in=questiongroup_ids).distinct(
            'institution_id').values_list(
            'institution_id', flat=True)
    # schools = AnswerGroup_Institution.objects.filter(
    #             institution__gp_id=gp_id).filter(
    #                 questiongroup__survey_id=survey_id
    #             ).filter(
    #         date_of_visit__year__gte=from_datetime_obj.year).filter(
    #         date_of_visit__year__lte=to_datetime_obj.year).filter(
    #         date_of_visit__month__gte=from_datetime_obj.month).filter(
    #         date_of_visit__month__lte=to_datetime_obj.month).filter(
    #             questiongroup_id__in=distinct_qgroups).distinct(
    #                 'institution_id').values_list(
    #                 'institution_id', flat=True)
    schools_info = {}
    print("Participating Schools count is: ", schools.count())
    for school in schools:
        start2 = time.time()
        school_report = get_school_report(school, survey_id, from_yearmonth, to_yearmonth)
        end2 = time.time()
        print("Time for school %s report = %s" % (school, end2-start2))
        schools_info[school] = school_report
    end = time.time()
    print("Total time to compute report for GP ID %s with %s schools = %s"
          % (gp_id, schools.count(), end-start))
    return schools_info
