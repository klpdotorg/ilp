from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg,
    GPStudentScoreGroups,
    GPSchoolParticipationCounts,
    GPContestSchoolDetails
)
from schools.models import Institution
from assessments.models import (
    Survey,
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg, CompetencyOrder,
    SurveyBoundaryQuestionGroupAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyEBoundaryQuestionGroupAnsAgg
    )
from boundary.models import (
    Boundary, ElectionBoundary
)
from django.db.models import Sum
from collections import OrderedDict
from .utils import convert_to_academicyear
import locale
'''
This method gets called even with boundary ids that don't have any gp contest
at all. So method has to account for those cases.
'''
def get_details(gp_survey_id, boundary_id, boundary_type_id,
                    from_yearmonth, to_yearmonth):
    """
        Returns a report dict for one boundary
    """
    # This is to add the commas in the right places in the numbers
    # SEtting it to OR because that's installed in almost all our systems
    # If locale is not installed, please install first
    # TODO: Should be added to our terraform, ansible config scripts
    locale.setlocale(locale.LC_NUMERIC, "en_IN")
    state_report = get_state_counts(gp_survey_id, from_yearmonth, to_yearmonth)
    boundary_report={}
    # Identify the type of boundary - election boundary or boundary
    if boundary_type_id == 'SD':
        try:
            district_report = get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        except:
            print("No GP contests in this district %s " % boundary_id)
            return None
        else:
            boundary_report["district"] = district_report
            boundary_report["state"] = state_report
            return boundary_report
    elif boundary_type_id == 'SB':
        id = Boundary.objects.get(id=boundary_id)
        try:
            district_report = get_boundary_info(id.parent_id, gp_survey_id, from_yearmonth, to_yearmonth)
            block_report = get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        except:
            print("No GP contests in this block %s and its associated district %s " % (boundary_id, id.parent_id))
            return None
        else:
            boundary_report["state"] = state_report
            boundary_report["district"] = district_report
            boundary_report["block"] = block_report
            return boundary_report
    else:
        # It is a GP
        try:
            gp_report = get_gp_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth)
        except:
            print("No GP contest held for this boundary %s " % boundary_id)
            return None
        else:
            # Now get the block and district info to which this GP belongs
            qs = Institution.objects.filter(gp_id=boundary_id)
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

def get_state_counts(gp_survey_id, from_yearmonth, to_yearmonth):
    state_level_counts = {}
    # Since survey id is unique per state, no need to filter explicitly
    # for state
    # State level counts computation
    survey = Survey.objects.get(id=gp_survey_id)
    state_counts = BoundaryCountsAgg.objects.get(boundary_id=survey.admin0)
    state_level_counts["state_name"] = survey.admin0.name
    total_children = locale.format("%d", state_counts.num_students,grouping=True)
    state_level_counts["num_students"] = total_children
    total_schools = locale.format("%d", state_counts.num_schools, grouping=True)
    #total_schools = "{:,}".format(state_counts.num_schools)
    state_level_counts["num_schools"] = total_schools
    state_level_counts["num_gps"] = locale.format("%d",state_counts.num_gps,grouping=True)
    return state_level_counts


def get_gp_info(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    try:
        eb = ElectionBoundary.objects.get(id=int(gp_id))
    except:
        print("Election boundary %s does not exist." % gp_id)
    else:
        gp_name = eb.const_ward_name
        gp_lang_name = eb.const_ward_lang_name
        gp_id = eb.id
        # Ideally you should just get ONE school here in the get
        try:
            num_schools = GPSchoolParticipationCounts.objects\
                .filter(yearmonth__gte=from_yearmonth) \
                    .filter(yearmonth__lte=to_yearmonth) \
                        .filter(gp_id=eb.id).aggregate(total_schools=Sum("num_schools"))
        except:
            print("Error finding GP %s in GPSchoolParticipationCounts table" % gp_id)
        try:
            num_children = GPStudentScoreGroups.objects \
                .filter(yearmonth__gte=from_yearmonth) \
                    .filter(yearmonth__lte=to_yearmonth) \
                        .filter(gp_id=gp_id).aggregate(total_children=Sum("num_students"))
        except:
            print("Error finding GP %s in GPStudentScoreGroups table" % gp_id)
        gp_info = {}
        try:
            gp_details = GPContestSchoolDetails.objects.get(gp_id=int(gp_id))
        except:
            print("Unable to get gp details " % gp_id)
        else:
            gp_info["block_name"] = gp_details.block_name
            gp_info["district_name"] = gp_details.district_name
       
        gp_info["name"] = gp_name
        gp_info["lang_name"] = gp_lang_name
        gp_info["num_schools"] = locale.format("%d",num_schools["total_schools"],grouping=True)
        if num_children is not None:
            gp_info["num_students"] = locale.format("%d",num_children["total_children"],grouping=True)
        else:
            gp_info = None
        return gp_info


def get_boundary_info(boundary_id, gp_survey_id, from_yearmonth, to_yearmonth):
    try:
        b = Boundary.objects.get(id=boundary_id)
    except:
        print("boundary id %s does not exist in DB " % boundary_id)
        return
    else:
        boundary_type = b.boundary_type_id
        boundary_counts = None
        # NEed the year to pass to the boundary counts agg table
        acadyear = convert_to_academicyear(from_yearmonth, to_yearmonth)
        # Boundary level counts
        try:
            boundary_counts = get_boundary_counts(boundary_id, acadyear)
        except:
            print("boundary id %s does not have any results for the given params " % boundary_id)
        return boundary_counts

def get_boundary_counts(boundary_id, academic_year):
    #academic_year is of the format 1819, 1920 etc..
    boundary_counts = BoundaryCountsAgg.objects.filter(academic_year=str(academic_year)).get(boundary_id=boundary_id)
    b = Boundary.objects.get(id=boundary_id)
    boundary_details={}
    boundary_details["parent_boundary_name"] = b.parent.name
    boundary_details["parent_langname"] = b.parent.lang_name
    boundary_details["num_blocks"] = locale.format("%d",boundary_counts.num_blocks,grouping=True)
    boundary_details["num_gps"] = locale.format("%d",boundary_counts.num_gps,grouping=True)
    boundary_details["num_schools"] = locale.format("%d",boundary_counts.num_schools,grouping=True)
    boundary_details["num_students"] = locale.format("%d",boundary_counts.num_students,grouping=True)
    boundary_details["boundary_name"] = boundary_counts.boundary_name
    boundary_details["boundary_langname"] = boundary_counts.boundary_lang_name
    boundary_details["boundary_id"] = boundary_counts.boundary_id.id
    boundary_details["boundary_type"] = boundary_counts.boundary_type_id.char_id
    return boundary_details