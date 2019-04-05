from reports.gp_hardcopy_reports.generate_report import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_gp_summary(1035, 2, "2018-06-01", "2019-03-31")
    print(gradewise)
    print("=================================================")
