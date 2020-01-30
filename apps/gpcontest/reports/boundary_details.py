from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg
)
from assessments.models import (
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg, CompetencyOrder
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
        boundary_counts = BoundaryCountsAgg.objects.get(boundary_id=boundary_id)
        boundary_report["parent_boundary_name"] = b.parent.name
        boundary_report["parent_langname"] = b.parent.lang_name
        boundary_report["num_blocks"] = boundary_counts.num_blocks
        boundary_report["num_gps"] = boundary_counts.num_gps
        boundary_report["num_schools"] = boundary_counts.num_schools
        boundary_report["num_students"] = boundary_counts.num_students
        boundary_report["boundary_name"] = boundary_counts.boundary_name
        boundary_report["boundary_langname"] = boundary_counts.boundary_lang_name
        boundary_report["boundary_id"] = boundary_counts.boundary_id.id
        boundary_report["boundary_type"] = boundary_counts.boundary_type_id.char_id
    return boundary_report 
