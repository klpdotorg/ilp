from gpcontest.reports.school_compute_numbers import *


def run():
    print("GP School report summary")
    scores = get_gp_schools_report(6114, 2, '201806', '201903')
    print(scores)
    # Test individual school report
    print("Testing individual school report")
    result = get_school_report(25844, 2, '201806', '201903')
    print(result)
    print("=================================================")

   
