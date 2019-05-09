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
    GPInstitutionClassQDetailsAgg,
    GPInstitutionDeficientCompetencyPercentagesAgg,
    GPContestSchoolDetails
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
                                   contest_yearmonth):
    """
        Return a dictionary with the questiongroup_name and
        array of 3 question keys (competencies) less than 60%
        that the class is most deficient in. The return dict is of the format:
        {
            "Class 4 Assessment": [
                {"competency": 'Addition', "local_name": "xxx in Kannada"}
                {"competency":'Subtraction', "local_name": "xxx in Kannada"}, 
                {"competency": 'Multiplication', "local_name": "xxx in Kannada}
            ],
            Questiongroup2_Name: [xx,yy,xx],
            .....
        }
    """
    queryset = GPInstitutionDeficientCompetencyPercentagesAgg.objects.filter(
        institution_id=school_id).filter(
            questiongroup_id=questiongroup_id
        ).filter(yearmonth=contest_yearmonth)
    competency_map = {}
    # Stick the competencies and their percentages in a dict so as to compute
    # the three lowest percentage scores
    for each_row in queryset:
        competency_map[each_row.question_key] = each_row.percent_score
    three_smallest = nsmallest(3, competency_map, key=competency_map.get)
    deficiencies = []
    # Fetch the local lang name from the mvw
    for key in three_smallest:
        qs = queryset.filter(question_key=key)
        # Just fetch the local lang name from any row of the filtered qs
        local_lang_name = qs[:1].get().lang_question_key
        deficiencies.append(
            {"competency": key,
             "local_name": local_lang_name}
            )
    return deficiencies


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

    date_of_contest, yearmonth_dates = get_date_of_contest(
        survey_id, from_yearmonth, to_yearmonth, school_id=school_id)  
    result = {}
    try:
        school_info = GPContestSchoolDetails.objects.get(
            institution_id=school_id)
    except:
        print("unable to fetch school info for school ID %s" % school_id)
        print("Skipping generation of reports for school ID %s" % school_id)
    else:
        for index,date in enumerate(yearmonth_dates):
            school_data = {}
            #import pdb; pdb.set_trace()
            queryset = GPInstitutionClassQDetailsAgg.objects.filter(
                institution_id=school_info.institution_id).filter(yearmonth=date)
            # Get questiongroups applicable for this survey ID 
            # for the given contest date
            questiongroup_ids = get_questiongroups_survey_for_contestdate(
                survey_id,
                school_info.gp_id.id, date)
            school_data["school_id"] = school_info.institution_id.id
            school_data["school_name"] = school_info.institution_name
            school_data["dise_code"] = school_info.school_code
            school_data["district_name"] = school_info.district_name
            school_data["block_name"] = school_info.block_name
            school_data["cluster_name"] = school_info.cluster_name
            school_data["gp_id"] = school_info.gp_id.id
            school_data["gp_name"] = school_info.gp_name
            school_data["date"] = date
            for each_class in questiongroup_ids:
                try:
                    class_participation =\
                        GPInstitutionClassParticipationCounts.objects.filter(
                            institution_id=school_id).filter(
                                questiongroup_id=each_class).get(yearmonth=date)
                except GPInstitutionClassParticipationCounts.DoesNotExist:
                    print("This GP does not have class %s" % each_class)
                else:
                    if class_participation is not None:
                        num_students = class_participation.num_students
                    # Find the lowest 3 competencies below 60% for each class of this
                    # school
                    deficiencies = compute_deficient_competencies(
                                    school_id, each_class, survey_id,
                                    date)
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
                                int(answer.correct_answers)
                            question_answer_details["percent"] = \
                                float(answer.percent_score)
                            class_questions.append(question_answer_details)
                        class_details["question_answers"] = class_questions
                        qgroup = QuestionGroup.objects.get(id=each_class)
                        # Check if a class exists because sometimes it might
                        #  not for
                        # a particular school
                        if deficiencies is not None:
                            class_details["deficiencies"] = deficiencies
                        school_data[qgroup.name] = class_details
            result[date_of_contest[index]] = school_data
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
    questiongroup_ids = get_all_qgroups_survey(
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
