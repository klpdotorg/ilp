from .gp_compute_numbers import *
from assessments.models import (
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    QuestionGroup)
from .utils import *


def get_questiongroups_survey(survey_id, from_yearmonth, to_yearmonth):
    # First convert the date to an academic year format required
    # by the QuestionGroup table
    academic_year = convert_to_academicyear(from_yearmonth, to_yearmonth)
    """ This returns a list of questiongroup ids for a particular
    academic year and survey.Year has to be of format 1819 or 1718 """
    return QuestionGroup.objects.filter(survey_id=survey_id).filter(
        academic_year_id=str(academic_year)
    ).distinct('id').values_list('id', flat=True)


def get_gps_for_academic_year(gpcontest_survey_id, from_yearmonth, to_yearmonth):
    """ Returns a list of distinct gp_ids for the academic year 
    where gp contest happened """
    return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=gpcontest_survey_id
    ).filter(
        yearmonth__gte=from_yearmonth, yearmonth__lte=to_yearmonth
        ).distinct().values_list('eboundary_id', flat=True)


def generate_all_reports(gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for ALL GPs in a given time frame for which
    we have data in our DB """
    #from_yearmonth, to_yearmonth = convert_to_yearmonth(from_yearmonth, to_yearmonth)
    gp_ids = get_gps_for_academic_year(gp_survey_id, from_yearmonth,
                                       to_yearmonth)
    result = generate_for_gps_list(gp_ids, gp_survey_id, from_yearmonth,
                                   to_yearmonth)
    return result
   

def generate_for_gps_list(list_of_gps, gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for an array of GP ids """
    all_gps = {
        "count": len(list_of_gps),
    }
    for gp in list_of_gps:
        gp_dict = generate_gp_summary(gp, gp_survey_id, from_yearmonth, to_yearmonth)
        all_gps[gp] = gp_dict
        #Call school report code
        #Pass resulting dicts into templates
    return all_gps

def generate_gp_summary(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    """
        Take a gp contest survey id and date range in the format of
        YYYY-MM-DD and generate a report
    """
    # Get basic GP info such as district/block/cluster/num students/schools
    #  etc..
    num_schools = get_participating_school_count(
                                                gp_id,
                                                gp_survey_id,
                                                from_yearmonth,
                                                to_yearmonth)
    try:
        gp = ElectionBoundary.objects.get(id=gp_id)
    except:
        print("Invalid GP %s. Does not exist in DB" % gp_id)
        raise ValueError("Invalid GP %s. Does not exist in DB" % gp_id)
    else:
        gp_name = gp.const_ward_name
    
    # TODO: Move this out to the top level function. Need not be calculated
    # per GP
    # Get questiongroups applicable for this survey ID for the given year range
    questiongroup_ids = get_questiongroups_survey(
                                                    gp_survey_id,
                                                    from_yearmonth,
                                                    to_yearmonth)
    
    # Get general GP info. Needs to be calculated per GP because block/cluster
    # info might be different per GP
    schools = Institution.objects.filter(gp_id=gp_id)
    if schools.count() > 0:
        district_name = Boundary.objects.get(id=schools.first().admin1_id).name
        block_name = Boundary.objects.get(id=schools.first().admin2_id).name
        cluster_name = Boundary.objects.get(id=schools.first().admin3_id).name
    else:
        print("Can't find schools for the GP  ID %s. District/Block/Cluster will be empty" % gp_id)
        district_name = ""
        block_name = ""
        cluster_name = ""
    #Compute score categories for students
    all_score_buckets = get_gradewise_score_buckets(
        gp_id, questiongroup_ids, from_yearmonth, to_yearmonth)
    class4 = None
    class5 = None
    class6 = None
    gp_num_students = 0  # Variable to hold total # of students in GP contest
    all_scores_for_gp = {
        "gp_name": gp_name,
        "num_schools": num_schools,
        "district": district_name,
        "block": block_name,
        "cluster": cluster_name,
    }
    for questiongroup in questiongroup_ids:
        qgroup = QuestionGroup.objects.get(id=questiongroup)
        all_scores_for_gp[qgroup.name] = {}
        total_answers = get_total_assessments_for_grade(gp_id, questiongroup,
                                                        gp_survey_id,
                                                        from_yearmonth,
                                                        to_yearmonth)
        answers = get_grade_competency_correctscores(
                gp_id, questiongroup, gp_survey_id, from_yearmonth, to_yearmonth
                )
        result = format_answers(total_answers, answers)
        result["total"] = all_score_buckets[qgroup.name]["total"]
        # Add participating students in each grade to get total students in
        # GP contest
        gp_num_students = gp_num_students + int(result["total"])
        all_scores_for_gp[qgroup.name]["competency_scores"] = result
        all_scores_for_gp[qgroup.name]["overall_scores"] = all_score_buckets[qgroup.name]
        if "class 6" in qgroup.name.lower():
            percentage = get_grade_competency_percentages(
                                            gp_id, questiongroup,
                                            gp_survey_id,
                                            from_yearmonth, to_yearmonth)
            all_scores_for_gp[qgroup.name]["percent_scores"] = percentage
        all_scores_for_gp["num_students"] = gp_num_students
    return all_scores_for_gp


def get_total_answers_for_qkey(qkey, queryset):
    return queryset.get(question_key=qkey)["total_answers"]


def format_answers(total_answers_qs, correct_ans_queryset):
    competency_scores = {}
    for each_row in correct_ans_queryset:
        competency_scores[each_row["question_key"]] =\
            each_row["correct_answers"]
    return competency_scores

   