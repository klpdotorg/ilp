from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg
)

def generate_boundary_report(
                            gp_survey_id, boundary_id,
                            from_yearmonth, to_yearmonth):
    # Identify the type of boundary - SD(district) or SB (block)
    report = {}
    boundary_stu_score_groups =\
        BoundaryStudentScoreGroups.objects.filter(boundary_id=boundary_id)
    boundary_counts = BoundaryCountsAgg.objects.filter(boundary_id=boundary_id)
    report["num_blocks"] = boundary_counts.num_blocks
    report["num_gps"] = boundary_counts.num_gps
    report["num_schools"] = boundary_counts.num_schools
    report["num_students"] = boundary_counts.num_students
    report["boundary_name"] = boundary_counts.boundary_name
    report["boundary_id"] = boundary_counts.boundary_id
    report["boundary_type"] = boundary_counts.boundary_type_id
    # Each row is basically a questiongroup or class
    for each_row in boundary_stu_score_groups:
        overall_scores = {}
        overall_scores["total"] = each_row.num_students
        overall_scores["below35"] = each_row.cat_a
        overall_scores["35to60"] = each_row.cat_b
        overall_scores["60to75"] = each_row.cat_c
        overall_scores["75to100"] = each_row.cat_d
        report[each_row.questiongroup_name]["overall_scores"] = overall_scores
    return report
        
