import datetime
import csv
import sys


from reports.reports import ReportOne,GPMathContestReport
from reports.models import Reports
from .reportlist import reportlist
from .contacts import contacts
from common.utils import send_sms

def send_link(dry, filepath, gp_name):
    print('start')
    frequency_str = '1,16,17,18'
    r_type = 'GPMathContestReport'
    params = {'gp_name': gp_name, 'academic_year': '2017-2018'}

    frequency = frequency_str.split(',')
    today = datetime.datetime.now().strftime("%d")

    report_status = True
    for d in frequency:
        if d==today:
            print('Scheduled {} for {} panchayat sending now'.format(r_type,gp_name))
            report_status = False
            r = reportlist[r_type]
            report = r(**params)
            report.get_data()
            result = report.save()
            
            with open(filepath, 'rt') as f:
                reader = csv.reader(f)
                for person in reader:
                    link = report.save_link(result)
                    sms = report.get_sms(link.track_id,person[0])
                    if(dry):
                        print('send sms to {}, phone: {}'.format(person[0],person[1]))
                    else:
                        print(person[1],sms)
                        # send_sms(person['number'],sms)
    if report_status:
        print("No reports scheduled today")
