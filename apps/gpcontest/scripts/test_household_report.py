from gpcontest.reports.household_report import *


def run():
    print("Household report summary")
    scores = get_HHReport_for_boundary(7, 3072, '201806', '201903')
    print(scores)
