from gpcontest.reports.generate_report import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_gp_summary(1035, 2, "201806", "201903")
    print(gradewise)
    print("=================================================")
