from gpcontest.reports.school_compute_numbers import *


def run():
    print("SCHOOL REPORT SUMMARY")
    scores = compute_deficient_competencies(13876, 2, '201806', '201903')
    print(scores)
    print("=================================================")
