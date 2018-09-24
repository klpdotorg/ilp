def calc_stud_performance(scores):
    # Calculate the perfomance of students
    boys_100 = 0
    girls_100 = 0
    boys_zero = 0
    girls_zero = 0
    for i in scores.values():
        total = sum(i['mark'])/len(i['mark'])
        if total == 100.0:
            if i['gender'] == 'Male':
                boys_100 += 1
            else:
                girls_100 += 1
        elif total == 0.0:
            if i['gender'] == 'Male':
                boys_zero += 1
            else:
                girls_zero += 1

    score_100 = boys_100 + girls_100
    score_zero = boys_zero + girls_zero
    return score_100, score_zero
