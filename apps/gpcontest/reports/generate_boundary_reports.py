from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg
)
from assessments.models import (
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg, CompetencyOrder,
    AnswerGroup_Institution
)
from boundary.models import (
    Boundary
)
from django.db.models import Sum
from collections import OrderedDict
from .utils import convert_to_academicyear
import locale
# This is to add the commas in the right places in the numbers
# SEtting it to OR because that's installed in almost all our systems
# If locale is not installed, please install first
# TODO: Should be added to our terraform, ansible config scripts

locale.setlocale(locale.LC_NUMERIC, "en_IN")

def generate_all_district_reports(
        gp_survey_id, from_yearmonth, 
        to_yearmonth, include_childboundary_reports=False):
    """
    For a given survey ID, generate reports for all districts that participated
    in a time frame and include block reports if include_childboundary_reports
    is True. 
    """
    district_ids = get_districts_for_survey(gp_survey_id, from_yearmonth,
                                            to_yearmonth)
    reports = generate_boundary_reports(
                            gp_survey_id, district_ids, from_yearmonth,
                            to_yearmonth, include_childboundary_reports)
    return reports


def generate_all_block_reports(
        gp_survey_id, from_yearmonth, 
        to_yearmonth):
    """ Generate ONLY block reports for a given time frame and survey ID """
    block_ids = get_blocks_for_survey(
                                    gp_survey_id, from_yearmonth,
                                    to_yearmonth)
    reports = generate_boundary_reports(
                            gp_survey_id, block_ids, from_yearmonth,
                            to_yearmonth)
    return reports


def generate_block_reports_for_district(
        gp_survey_id, list_district_ids, from_yearmonth, 
        to_yearmonth):
    """ Generate ONLY block reports for a given district """
    block_ids = []
    for d in list_district_ids:
        blocks = get_blocks_for_district(
                            d, gp_survey_id, from_yearmonth,
                            to_yearmonth)
        block_ids.extend(blocks)
    reports = generate_boundary_reports(
                        gp_survey_id, block_ids, from_yearmonth,
                        to_yearmonth)
    return reports

def generate_boundary_reports(
    gp_survey_id, list_boundary_ids, from_yearmonth, 
        to_yearmonth, include_childboundary_reports=False):
    """ Generate district and associated block reports if 
    include_childboundary_reports = True and return all in a giant dict.
    Else just generate district reports in dict and return """
    final_report = {}
    for boundary in list_boundary_ids:
        try:
            boundary_obj= Boundary.objects.get(id=boundary)
        except:
            print("No boundary ID %s exists in the DB" % boundary)
            return None
        else:
            boundary_type_id = boundary_obj.boundary_type_id
            boundary_dict = generate_boundary_report(gp_survey_id, 
                                    boundary, from_yearmonth, to_yearmonth)
            # IF its a district and the flag is True, generate block reports
            if include_childboundary_reports and boundary_type_id == 'SD' and boundary_dict:
                boundary_dict["blocks"] = {}
                block_ids = get_blocks_for_district(boundary, gp_survey_id, from_yearmonth, to_yearmonth)
                for block in block_ids:
                    block_dict = generate_boundary_report(gp_survey_id, block, from_yearmonth, to_yearmonth)
                    boundary_dict["blocks"][block] = block_dict
        final_report[boundary] = boundary_dict
    return final_report

def generate_boundary_report(
                            gp_survey_id, boundary_id,
                            from_yearmonth, to_yearmonth):
    """
        Returns a report dict for one boundary
    """
    # Identify the type of boundary - SD(district) or SB (block)
    try:
        b = Boundary.objects.get(id=boundary_id)
    except:
        print("boundary id %s does not exist in DB " % boundary_id)
        return
    else:
        boundary_type = b.boundary_type_id
        boundary_report = {}
        # Need the year to pass to the boundary counts agg table
        acadyear = convert_to_academicyear(from_yearmonth, to_yearmonth)
        boundary_stu_score_groups =\
            BoundaryStudentScoreGroups.objects.filter(
                boundary_id=boundary_id).filter(
                    yearmonth__gte=from_yearmonth
                ).filter(
                    yearmonth__lte=to_yearmonth
                ).values('boundary_id', 'boundary_name','questiongroup_name','questiongroup_id').annotate(total_cat_a=Sum("cat_a"),
                total_cat_b=Sum("cat_b"), total_cat_c=Sum("cat_c"), total_cat_d=Sum("cat_d"),
                total_num_students=Sum("num_students"))
        try:
            boundary_counts = BoundaryCountsAgg.objects.filter( \
                yearmonth__gte=from_yearmonth, yearmonth__lte=to_yearmonth).filter(
                    boundary_id=boundary_id).values('boundary_id','boundary_name','boundary_lang_name','boundary_type_id')
            #boundary_numblocks = boundary_counts.annotate(blocks=Sum('num_blocks'))[0]
            boundary_numschools = boundary_counts.annotate(schools=Sum('num_schools'))[0]
            boundary_numstudents = boundary_counts.annotate(students=Sum('num_students'))[0]
            boundary_numgps = boundary_counts.annotate(gps=Sum('num_gps'))[0]
        except:
            print("No boundary counts for boundary id %s in DB" % b.id)
        else:
            boundary_report["parent_boundary_name"] = b.parent.name
            boundary_report["parent_langname"] = b.parent.lang_name
            boundary_report["num_blocks"] = "NA"
            boundary_report["num_gps"] = "NA"
            boundary_report["num_schools"] = "NA"
            boundary_report["num_students"] = "NA"
            if boundary_type == 'SD':
                block_ids = get_blocks_for_district(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
                boundary_report["num_blocks"] = locale.format("%d", block_ids.count(), grouping=True)
            if boundary_numgps:
                boundary_report["num_gps"] = locale.format("%d", boundary_numgps["gps"], grouping=True)
            if boundary_numschools:
                boundary_report["num_schools"] = locale.format("%d", boundary_numschools["schools"], grouping=True)
            if boundary_numstudents:
                boundary_report["num_students"] = locale.format("%d",boundary_numstudents["students"],grouping=True)
            boundary_report["boundary_name"] = boundary_counts[0]["boundary_name"]
            boundary_report["boundary_langname"] = boundary_counts[0]["boundary_lang_name"]
            boundary_report["boundary_id"] = boundary_counts[0]["boundary_id"]
            boundary_report["boundary_type"] = boundary_counts[0]["boundary_type_id"]
            competency_scores = get_competency_scores_for_all_qgroups(
                gp_survey_id, boundary_id, from_yearmonth, to_yearmonth
            )
            # Each row is basically a questiongroup or class
            for each_row in boundary_stu_score_groups:
                boundary_report[each_row["questiongroup_name"]] = {}
                overall_scores = {}
                overall_scores["total"] = each_row["total_num_students"]
                overall_scores["below35"] = each_row["total_cat_a"]
                overall_scores["35to60"] = each_row["total_cat_b"]
                overall_scores["60to75"] = each_row["total_cat_c"]
                overall_scores["75to100"] = each_row["total_cat_d"]
                boundary_report[each_row["questiongroup_name"]]["overall_scores"] = \
                    overall_scores

                # Find the competency scores
                competencies = competency_scores.filter(
                                    questiongroup_name=each_row["questiongroup_name"])
                concept_scores = format_answers(each_row["questiongroup_id"], competencies)
                concept_scores["total"] = each_row["total_num_students"]
                boundary_report[each_row["questiongroup_name"]]["competency_scores"] = \
                    concept_scores
                if each_row["questiongroup_name"] == "Class 6 Assessment":
                    boundary_report["percent_scores"] = {"Class 6 Assessment": {}}
                    percs = get_grade_competency_percentages(
                        competency_scores, boundary_id, each_row["questiongroup_name"],
                        gp_survey_id, from_yearmonth, to_yearmonth)
                    boundary_report["percent_scores"][each_row["questiongroup_name"]] = \
                        percs
            return boundary_report


def get_grade_competency_percentages(
        correct_answers_qset, boundary_id, qgroup_name, gpcontest_survey_id,
        report_from, report_to):
    """
        Computes the percentage of students who are fluent in a competency
        in the given time frame, survey_id and the Gram Panchayat
        id. Returns a queryset which can be further filtered or manipulated
    """
    correct_answers_agg = correct_answers_qset
    total_assessments = get_total_assessments_for_grade(boundary_id, qgroup_name,
                                                        gpcontest_survey_id,
                                                        report_from,
                                                        report_to)
    results_by_date = {}
    concept_scores = {
            "Number Recognition": 'NA',
            "Place Value": 'NA',
            "Addition": 0,
            "Subtraction": 0,
            "Multiplication": 0,
            "Division": 0
        }
    if total_assessments is not None and correct_answers_agg is not None: 
        correct_ans_for_date = correct_answers_agg.filter(questiongroup_name=qgroup_name)
        for each_row in total_assessments:
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
    return concept_scores


def get_competency_scores_for_all_qgroups(
        gpcontest_survey_id, boundary_id, from_yearmonth, to_yearmonth):
    """
        Returns competency correct score queryset for all grades for a given
        boundary id. Filter the relevant grade (questiongroup name) from here
        for usage.report_from and report_to are
        yearmonth formats
    """
    correct_answers_agg = None
    try:
        correct_answers_agg = \
            SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
            .filter(survey_id=gpcontest_survey_id,
                    boundary_id=boundary_id, survey_tag='gka')\
            .filter(yearmonth__gte=from_yearmonth)\
            .filter(yearmonth__lte=to_yearmonth)\
            .values('question_key', 'questiongroup_name')\
            .annotate(correct_answers=Sum('numcorrect'))
    except SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
        pass
    return correct_answers_agg


def get_total_assessments_for_grade(boundary_id, qgroup_name, gpcontest_survey_id,
                                    report_from, report_to):
    """
        Returns total assessments for a given questiongroup name or class. 
        Currently only computed for Class 6 (qgroup_name param). report_from 
        and report_to are yearmonth formats
    """
    total_assessments = None
    try:
        total_assessments = SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
                .filter(survey_id=gpcontest_survey_id,
                        boundary_id=boundary_id, survey_tag='gka')\
                .filter(questiongroup_name=qgroup_name)\
                .filter(yearmonth__gte=report_from)\
                .filter(yearmonth__lte=report_to)\
                .values('question_key')\
                .annotate(total_answers=Sum('numtotal'))
    except SurveyBoundaryQuestionGroupQuestionKeyAgg.DoesNotExist:
        pass
    return total_assessments


def format_answers(questiongroup_id, correct_ans_queryset):
    # Note that below set of competencies is hardcoded. If the template
    # changes we would need to change this. Doing this in lieu of a mat view
    # that will contain rows of competencies taht didn't have a correct ans
    # score.

    competencies = ["Addition", "Subtraction", "Number Recognition",
                    "Place Value", "Multiplication", "Division"]            
    competencies_in_db = CompetencyOrder.objects.filter(questiongroup=questiongroup_id).order_by('sequence').values_list('key', flat=True)
    competency_scores = {}
    for competency in competencies:
        # This competency is NA for this class. Hence assign NA to it
        if competency not in competencies_in_db:
            competency_scores[competency] = 'NA'
        else:
            try:
                each_row = correct_ans_queryset.get(question_key=competency)
            except:
                each_row = None
            if each_row is not None:
                correctans = each_row["correct_answers"]
                if correctans is None:
                    correctans = 0
                competency_scores[competency] =\
                    correctans
            # No one got this answer right, send 0 back
            else:
                competency_scores[competency] = 0
    return competency_scores

def get_districts_for_survey(survey_id, from_yearmonth, to_yearmonth):
    """ Returns all districts which have data for a given time range and
    survey id """
    return SurveyBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=survey_id).filter(
                        boundary_id__boundary_type_id__char_id='SD').distinct(
                            'boundary_id').values_list(
                                'boundary_id', flat=True)

def get_blocks_for_survey(survey_id, from_yearmonth, to_yearmonth):
    """ Returns all districts which have data for a given time range and
    survey id """
    return SurveyBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=survey_id).filter(
                        boundary_id__boundary_type_id__char_id='SB').distinct(
                            'boundary_id').values_list(
                                'boundary_id', flat=True)

def get_blocks_for_district(district_id, survey_id, from_yearmonth, to_yearmonth):
    return SurveyBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        yearmonth__gte=from_yearmonth).filter(
            yearmonth__lte=to_yearmonth).filter(
                survey_id=survey_id).filter(
                    boundary_id__parent=district_id).distinct('boundary_id').values_list(
                        'boundary_id', flat=True
                    )