from gpcontest.reports.generate_report import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_gp_summary(538, 2, "201906", "202003")
    print(gradewise)
    print("=================================================")
