import sys
import csv

from .reportlist import reportlist
from .links import send_recipient


def generate_report_internal(report_type, filepath, report_from, report_to, dry, start_from, gka, gp, hhsurvey,config, quit_on_error):
    try:
        r = reportlist[report_type]
        with open(filepath, 'rt') as f:
            reader = csv.reader(f)
            res = send_recipient(report_type, report_from, report_to, reader, dry, start_from, gka, gp, hhsurvey,config,quit_on_error)
            for m in res['messages']:
                print(m)
            return(res['successfull'])
        print('success')
    except KeyError:
        sys.stderr.write("{} is not a valid report type\n".format(report_type))
        raise
    except ValueError :
        sys.stderr.write("Error in Report generation\n")
        raise

def generate_report(report_type, filename, report_from, report_to, dry, start_from, gka,gp,hhsurvey, config, quit_on_error):
    try:
        rid = generate_report_internal(report_type, filename, report_from, report_to, dry, start_from, gka,gp,hhsurvey,config,quit_on_error)
        print ("{} Report created and successfully sent".format(rid))

    except (KeyError, ValueError) as e:
        raise

