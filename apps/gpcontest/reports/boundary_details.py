"""
This code was primarily written to help generate summaries for the letters
of appreciation to be sent out per district/block/GP. The APIs in this file
return summary counts of blocks/districts/GPs -- num_students, num_schools,
names of the boundaries etc..
"""
from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg,
    GPStudentScoreGroups,
    GPSchoolParticipationCounts
)
from schools.models import Institution
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

"""
Primary API called from outside
"""
def get_details(gp_survey_id, boundary_id, boundary_type_id,
                    from_yearmonth, to_yearmonth):
    """
        Returns a report dict for one boundary
    """
    state_report = get_state_counts(gp_survey_id, from_yearmonth, to_yearmonth)
    boundary_report={}
    # Identify the type of boundary - election boundary or boundary
    if boundary_type_id == 'SD':
        # if boundary is a district, fill in state and district info
        district_report = get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        boundary_report["district"] = district_report
        boundary_report["state"] = state_report
    elif boundary_type_id == 'SB':
        #If boundary is a block, fill in state, block, district info
        id = Boundary.objects.get(id=boundary_id)
        district_report = get_boundary_info(id.parent_id, gp_survey_id, from_yearmonth, to_yearmonth)
        block_report = get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        boundary_report["state"] = state_report
        boundary_report["district"] = district_report
        boundary_report["block"] = block_report
    else:
        # It is a GP. Fill in state, district, block, gp info
        gp_report = get_gp_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        # Now get the block and district info to which this GP belongs
        qs = Institution.objects.filter(gp_id=boundary_id)
        # Get any school that belongs to this GP and find the associated
        # district/block ids
        school = qs[0]
        district_id = school.admin1_id
        block_id = school.admin2_id
        district_report = get_boundary_info(district_id, gp_survey_id, from_yearmonth, to_yearmonth)
        block_report = get_boundary_info(block_id, gp_survey_id, from_yearmonth, to_yearmonth)
        boundary_report["state"] = state_report
        boundary_report["gp"] = gp_report
        boundary_report["district"] = district_report
        boundary_report["block"] = block_report
    return boundary_report

"""
Returns a dict with state level summaries. Since the gp survey id is
a state-specific id, no need to explicitly pass the state id separately
"""
def get_state_counts(gp_survey_id, from_yearmonth, to_yearmonth):
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
    return state_level_counts

"""
Returns GP info as a dict
"""
def get_gp_info(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    try:
        eb = ElectionBoundary.objects.get(id=gp_id)
    except:
        print("Election boundary %s does not exist." % gp_id)
    else:
        gp_name = eb.const_ward_name
        gp_lang_name = eb.const_ward_lang_name
        gp_id = eb.id
        # Ideally you should just get ONE school here in the get
        num_schools = GPSchoolParticipationCounts.objects\
            .filter(yearmonth__gte=from_yearmonth) \
                .filter(yearmonth__lte=to_yearmonth) \
                     .get(gp_id=gp_id).num_schools
        num_children = GPStudentScoreGroup.objects \
             .filter(yearmonth__gte=from_yearmonth) \
                .filter(yearmonth__lte=to_yearmonth) \
                     .get(gp_id=gp_id).num_children
        gp_info = {}
        gp_info["name"] = gp_name
        gp_info["lang_name"] = gp_lang_name
        gp_info["num_schools"] = num_schools
        gp_info["num_children"] = num_children
        return gp_info

"""
Returns a boundary's summary as a dict
"""
def get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth):
    try:
        b = Boundary.objects.get(id=boundary_id)
    except:
        print("boundary id %s does not exist in DB " % boundary_id)
        return
    else:
        boundary_type = b.boundary_type_id
        boundary_stu_score_groups =\
            BoundaryStudentScoreGroups.objects.filter(boundary_id=boundary_id)
        # Boundary level counts
        boundary_counts = get_boundary_counts(boundary_id)
        return boundary_counts

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