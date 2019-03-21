from reports.gp_hardcopy_reports.gp_compute_numbers import *


def run():
    print("GRADEWISE SCORE BUCKETS SUMMARY")
    scores = get_gradewise_score_buckets(1035, ['Class 4 Assessment', 'Class 5 Assessment', 'Class 6 Assessment'])
    print(scores)
    print("=================================================")

    print("# OF CHILDREN WHO ANSWERED CORRECTLY IN EACH GRADE")
    correct_scores = get_gradewise_competency_correctscores(1035, 2, 201706, 201803)
    for item in correct_scores:
        print(item)
    print("=================================================")

    print("OVERALL COMPETENCY PERCENTAGES IN GP:")
    percentages = get_gp_competency_percentages(1035, 2,
                                        201706, 201803)
    print(percentages)
    print("=================================================")
