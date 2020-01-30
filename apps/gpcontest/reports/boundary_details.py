from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg
)
from assessments.models import (
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg, CompetencyOrder,
    SurveyBoundaryQuestionGroupAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyEBoundaryQuestionGroupAnsAgg
    )
from boundary.models import (
    Boundary
)
from django.db.models import Sum
from collections import OrderedDict

def get_details(gp_survey_id, boundary_id,
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
        boundary_stu_score_groups =\
            BoundaryStudentScoreGroups.objects.filter(boundary_id=boundary_id)
        state_level_counts = {}
        # Since survey id is unique per state, no need to filter explicitly
        # for state
        # State level counts computation
        all_boundaries_per_state = SurveyBoundaryQuestionGroupAgg.objects.filter(survey_id=gp_survey_id) \
            .filter(yearmonth__gte=from_yearmonth) \
                .filter(yearmonth__lte=to_yearmonth)
        all_schools_per_state = SurveyInstitutionQuestionGroupAgg.objects.filter(survey_id=gp_survey_id) \
            .filter(yearmonth__gte=from_yearmonth) \
                .filter(yearmonth__lte=to_yearmonth)
        total_children = all_boundaries_per_state.aggregate(num_children=Sum("num_children"))
        state_level_counts["num_students"] = total_children["num_children"]
        total_schools = all_schools_per_state.distinct('institution_id') \
            .count()
        state_level_counts["num_schools"] = total_schools
        all_gps_per_state = SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(survey_id=gp_survey_id) \
            .filter(yearmonth__gte=from_yearmonth) \
                .filter(yearmonth__lte=to_yearmonth)
        total_gps = all_gps_per_state.distinct('eboundary_id').count()
        state_level_counts["num_gps"] = total_gps
        print(state_level_counts)
        boundary_report["state"] = state_level_counts
        boundary_report["district"] = {}
        boundary_report["block"] = {}
        boundary_report["gp"] = {}
        # Boundary level counts
        boundary_counts = get_boundary_counts(boundary_id)
        if boundary_type == 'SD':
            boundary_report["district"] = boundary_counts
        elif boundary_type == 'SB':
            boundary_report["district"] = get_boundary_counts(b.parent_id)
            boundary_report["block"] = boundary_counts
        elif boundary_type == 'GP':
            # TBD
            pass
    return boundary_report

def get_boundary_counts(boundary_id):
    boundary_counts = BoundaryCountsAgg.objects.get(boundary_id=boundary_id)
    b = Boundary.objects.get(id=boundary_id)
    boundary_details={}
    boundary_details["parent_boundary_name"] = b.parent.name
    boundary_details["parent_langname"] = b.parent.lang_name
    boundary_details["num_blocks"] = boundary_counts.num_blocks
    boundary_details["num_gps"] = boundary_counts.num_gps
    boundary_details["num_schools"] = boundary_counts.num_schools
    boundary_details["num_students"] = boundary_counts.num_students
    boundary_details["boundary_name"] = boundary_counts.boundary_name
    boundary_details["boundary_langname"] = boundary_counts.boundary_lang_name
    boundary_details["boundary_id"] = boundary_counts.boundary_id.id
    boundary_details["boundary_type"] = boundary_counts.boundary_type_id.char_id
    return boundary_details