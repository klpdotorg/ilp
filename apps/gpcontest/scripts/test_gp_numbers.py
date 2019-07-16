from gpcontest.reports.gp_compute_numbers import *


def run():
    print("GRADEWISE SCORE BUCKETS SUMMARY")
    scores = get_gradewise_score_buckets(1431, [45,46,47],201806, 201903)
    print(scores)
    print("=================================================")

    print("# OF CHILDREN WHO ANSWERED CORRECTLY IN EACH GRADE")
    correct_scores = get_gradewise_competency_correctscores(1431, 2, 201806, 201903)
    for item in correct_scores:
        print(item)
    print("=================================================")

    print("PERCENTAGES AT THE END OF 5 YEARS OF SCHOOLING IN GP:")
    percentages = get_grade_competency_percentages(1431,47,2,
                                        201806, 201903)
    print(percentages)
    print("=================================================")
