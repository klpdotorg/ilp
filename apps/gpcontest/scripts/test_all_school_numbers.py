from pandas_school_numbers_checker import *
from gpcontest.reports.generate_report import get_gps_for_academic_year


def run():
    #gps = get_gps_for_academic_year(2, 201806, 201903)
    gps=[1035]
    set_db_connection_params("ilp", "klp")
    for gp in gps:
        check_all_schools_in_gp(gp)
