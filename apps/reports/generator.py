import django_filters
from reports.reports import ReportOne, ReportTwo

reportlist = {"report_one":ReportOne,"report_two": ReportTwo}

def generate_report(report_format, report_type, output_name, *args):
    try:
        r = reportlist[report_type]
        report = r(*args)
        report.generate(report_format, output_name)
        report.save()
        print('success')
    except KeyError:
        print("Invalid report type")

    except AttributeError :
        print("Error in Report generation")
        raise 
