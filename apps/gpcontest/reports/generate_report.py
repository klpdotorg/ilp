from .gp_compute_numbers import *
from assessments.models import (
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    QuestionGroup)
from .utils import *


def get_gps_for_academic_year(gpcontest_survey_id):
    """ Returns a list of distinct gp_ids for the academic year 
    where gp contest happened """
    return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=gpcontest_survey_id
    ).distinct().values_list('eboundary_id', flat=True)


def generate_all_reports(gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for ALL GPs in a given time frame for which
    we have data in our DB """
    # rom_yearmonth, to_yearmonth = convert_to_yearmonth(from_yearmonth, to_yearmonth)
    gp_ids = get_gps_for_academic_year(gp_survey_id)
    result = generate_for_gps_list(gp_ids, gp_survey_id, from_yearmonth,
                                   to_yearmonth)
    return result


def generate_for_gps_list(list_of_gps, gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for an array of GP ids """
    all_gps = {
        "count": len(list_of_gps),
    }
    for gp in list_of_gps:
        try:
            gp_dict = generate_gp_summary(gp, gp_survey_id, from_yearmonth, to_yearmonth)
            all_gps[gp] = gp_dict
        except:
            print("Unable to generate report for GP ID %s. Please check other prints preceding this for something that went wrong" % gp)
            pass
    return all_gps


def get_date_of_contest(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    from_date, to_date = convert_yearmonth_to_fulldate(from_yearmonth, to_yearmonth)
    dates_of_contest = AnswerGroup_Institution.objects.filter(institution__gp_id=gp_id).filter(
        questiongroup__survey_id=gp_survey_id).filter(
            date_of_visit__range=[from_date, to_date]
        ).distinct('date_of_visit').values_list('date_of_visit', flat=True)
    formatted_dates = []
    for date in dates_of_contest:
        formatted_dates.append(date.strftime('%d/%m/%Y'))
    print("Dates of contest for GP %s are %s" % (gp_id, formatted_dates))
    return formatted_dates


def generate_gp_summary(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    """
        Take a gp contest survey id and date range in the format of
        YYYYMM and return a dictionary with GP summary data.
        Dict format is:
        
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
    contest_dates = get_date_of_contest(gp_id, gp_survey_id, from_yearmonth, to_yearmonth)
    all_scores_for_gp = {
        "gp_name": gp_name,
        "gp_id": gp_id,
        "num_schools": num_schools,
        "district": district_name,
        "block": block_name,
        "cluster": cluster_name,
        "date": contest_dates,
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
        # Need competency percentage scores only for Grade 6 per GP report
        # summary page format. So calculate below only for that
        if "class 6" in qgroup.name.lower():
            percentage = get_grade_competency_percentages(
                                            gp_id, questiongroup,
                                            gp_survey_id,
                                            from_yearmonth, to_yearmonth)
            all_scores_for_gp[qgroup.name]["percent_scores"] = percentage
        # Insert total number of students into the dict
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

   