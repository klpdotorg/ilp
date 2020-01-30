from gpcontest.reports.boundary_details import *


def run():
    print("Starting check of all GPs..")
    result = get_details(2, 420, 201906, 202003)
    print("DISTRICT result========")
    print(result)
    print("==============================")
    result = get_details(2, 496, 201906, 202003)
    print("BLOCK result=======")
    print(result)
    print("==============================")
    print("DONE")