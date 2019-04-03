from .gp_compute_numbers import *

def get_general_gp_info():


def generate_gp_report_for_latex():
    questiongroup_ids = [45, 46, 47]
    class4 = None
    class5 = None
    class6 = None
    for questiongroup in questiongroup_ids:
        total_answers = get_total_assessments_for_grade(1035, questiongroup,
                                                       2, 201806, 201903)
        answers = get_grade_competency_correctscores(
                1035, questiongroup, 2, 201806, 201903
                )
        result = format_answers(total_answers, answers)
        if questiongroup == 45:
            class4 = result
        elif questiongroup == 46:
            class5 = result
        elif questiongroup == 47:
            class6 = result
        print(result)



def get_total_answers_for_qkey(qkey, queryset):
    return queryset.get(question_key=qkey)["total_answers"]

def format_answers(total_answers_qs, correct_ans_queryset):
    competency_scores = {}
    for each_row in correct_ans_queryset:
        competency_scores[each_row["question_key"]] =\
            each_row["correct_answers"]
    return competency_scores

   