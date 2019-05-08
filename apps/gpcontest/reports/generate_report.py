from .gp_compute_numbers import *
from assessments.models import (
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    QuestionGroup)
from .utils import *


def get_gps_for_academic_year(
        gpcontest_survey_id,
        from_yearmonth,
        to_yearmonth):
    """ Returns a list of distinct gp_ids for the academic year 
    where gp contest happened """
    return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=gpcontest_survey_id
    ).filter(yearmonth__gte=from_yearmonth).filter(const_ward_type='GP').filter(
        yearmonth__lte=to_yearmonth).order_by(
            'eboundary_id').distinct().values_list(
            'eboundary_id', flat=True)


def generate_all_reports(gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for ALL GPs in a given time frame for which
    we have data in our DB """
    gp_ids = get_gps_for_academic_year(gp_survey_id, from_yearmonth, to_yearmonth)
    print("Count of gp_ids for which PDFs are to be generated: %s" % gp_ids.count())
    print("GPs for which report should be generated if data available is:")
    print(gp_ids)
    result = generate_for_gps_list(gp_ids, gp_survey_id, from_yearmonth,
                                   to_yearmonth)
    print(result)
    return result


def generate_for_gps_list(list_of_gps, gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for an array of GP ids """
    all_gps = {
        "count": len(list_of_gps),
    }
    schoolcount_by_assessment = get_schoolcount_classes_gplist(
                                    gp_survey_id, list_of_gps,
                                    from_yearmonth, to_yearmonth)
    all_gps["class4_num_schools"] = schoolcount_by_assessment["Class 4 Assessment"]
    all_gps["class5_num_schools"] = schoolcount_by_assessment["Class 5 Assessment"]
    all_gps["class6_num_schools"] = schoolcount_by_assessment["Class 6 Assessment"]
    all_gps["gp_info"] = {}
    for gp in list_of_gps:
        try:
            gp_dict = generate_gp_summary(gp, gp_survey_id, from_yearmonth, to_yearmonth)
            all_gps["gp_info"][gp] = gp_dict
        except Exception as e:
            print("%s (%s)" % (e, type(e)))
            # print("Unable to generate report for GP ID %s. Please check other prints preceding this for something that went wrong" % gp)
            pass
    return all_gps


def get_date_of_contest(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    from_date, to_date = convert_yearmonth_to_fulldate(from_yearmonth, to_yearmonth)
    dates_of_contest = AnswerGroup_Institution.objects.filter(institution__gp_id=gp_id).filter(
        questiongroup__survey_id=gp_survey_id).filter(
            date_of_visit__range=[from_date, to_date]
        ).distinct('date_of_visit').values_list('date_of_visit', flat=True)
    formatted_full_dates = []
    yearmonth_dates = []
    for date in dates_of_contest:
        formatted_full_dates.append(date.strftime('%d/%m/%Y'))
        yearmonth_dates.append(date.strftime('%Y%m'))

    print(formatted_full_dates)
    return formatted_full_dates, yearmonth_dates


def generate_gp_summary(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    """
        Take a gp contest survey id and date range in the format of
        YYYYMM and return a dictionary with GP summary data.
        Dict format is:    
    """
    contest_dates, yearmonth_dates = get_date_of_contest(gp_id, gp_survey_id, from_yearmonth, to_yearmonth)

    # Get basic GP info such as district/block/cluster/num students/schools
    #  etc..
    # Get participating schools count categorized by date of contest
    num_schools_by_contest_date = get_participating_school_count(
                                                gp_id,
                                                gp_survey_id,
                                                yearmonth_dates)
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
    # Compute score categories for students per contest-date. Return dict
    # is keyed by contest date
    all_score_buckets = get_gradewise_score_buckets(
        gp_id, questiongroup_ids, yearmonth_dates)
    class4 = None
    class5 = None
    class6 = None
    gp_num_students = 0  # Variable to hold total # of students in GP contest
    schoolcount_by_assessment_date = get_schoolcount_classes_count(
                                gp_survey_id, gp_id, from_yearmonth,
                                to_yearmonth,
                                yearmonth_dates)
    
    total_answers = get_total_assessments_for_grade(gp_id, questiongroup,
                                                                gp_survey_id,
                                                                from_yearmonth,
                                                                to_yearmonth)
    answers = get_grade_competency_correctscores(
                        gp_id, questiongroup, gp_survey_id, from_yearmonth, to_yearmonth
                        )
    data_by_contest_date = {}
    for date in yearmonth_dates:
        all_scores_for_gp = {
            "gp_name": gp_name,
            "gp_id": gp_id,
            "district": district_name,
            "block": block_name,
            "cluster": cluster_name,
            "date": contest_dates
        }
        num_schools = num_schools_by_contest_date.get(yearmonth=date)
        all_scores_for_gp["num_schools"] = num_schools
        if "Class 4 Assessment" in schoolcount_by_assessment:
            all_scores_for_gp["class4_num_schools"] = schoolcount_by_assessment[date]["Class 4 Assessment"]
        if "Class 5 Assessment" in schoolcount_by_assessment:
            all_scores_for_gp["class5_num_schools"] = schoolcount_by_assessment[date]["Class 5 Assessment"]
        if "Class 6 Assessment" in schoolcount_by_assessment:
            all_scores_for_gp["class6_num_schools"] = schoolcount_by_assessment[date]["Class 6 Assessment"]

        for questiongroup in questiongroup_ids:
            qgroup = QuestionGroup.objects.get(id=questiongroup) 
            # Check if
            if qgroup.name not in all_scores_for_gp:
                all_scores_for_gp[qgroup.name] = {}
                total_for_date = total_answers.filter(yearmonth=date)
                answers_for_contest = answers.filter(yearmonth=date)           
                # We've got answers and assessments for this particular GP for this
                # questiongroup ID
                if total_for_date is not None and answers_for_contest is not None:
                    result = format_answers(total_for_date, answers_for_contest)
                    result["total"] = all_score_buckets[date][qgroup.name]["total"]
                    # Add participating students in each grade to get total students in
                    # GP contest
                    gp_num_students = gp_num_students + int(result["total"])
                    all_scores_for_gp[qgroup.name]["competency_scores"] = \
                        result
                    all_scores_for_gp[qgroup.name]["overall_scores"] = \
                        all_score_buckets[date][qgroup.name]
                    # Need competency percentage scores only for Grade 6 per GP report
                    # summary page format. So calculate below only for that
                    if "class 6" in qgroup.name.lower():
                        percentage = get_grade_competency_percentages(
                                                        gp_id, questiongroup,
                                                        gp_survey_id,
                                                        from_yearmonth,
                                                        to_yearmonth)
                        all_scores_for_gp[qgroup.name]["percent_scores"] = \
                            percentage[date]
                    # Insert total number of students into the dict
                    all_scores_for_gp["num_students"] = gp_num_students
        data_by_contest_date[date] = all_scores_for_gp
    return data_by_contest_date


def get_total_answers_for_qkey(qkey, queryset):
    return queryset.get(question_key=qkey)["total_answers"]


def format_answers(total_answers_qs, correct_ans_queryset):
    # Note that below set of competencies is hardcoded. If the template
    # changes we would need to change this. Doing this in lieu of a mat view
    # that will contain rows of competencies taht didn't have a correct ans
    # score.
    competencies = ["Addition", "Subtraction", "Number Recognition",
                    "Place Value", "Multiplication", "Division"]
    competency_scores = {}
    for competency in competencies:
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
