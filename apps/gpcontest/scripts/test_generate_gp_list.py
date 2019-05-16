from gpcontest.reports.generate_report import *


def run():
    print("TEST GENERATE REPORT")
    gradewise = generate_for_gps_list([1431, 6114], 2, "201806", "201903")
    print(gradewise)
    print("=================================================")
