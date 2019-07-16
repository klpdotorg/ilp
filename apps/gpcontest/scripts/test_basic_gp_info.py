from gpcontest.reports.gp_compute_numbers import *


def run():
    print("BASIC GP INFO")
    try:
        gp_info = get_general_gp_info(1035, 1819)
    except ValueError as e:
        print(e)
    else:
        print(gp_info)
        print("=================================================")
