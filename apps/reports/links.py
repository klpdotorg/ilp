import datetime

from reports.reports import ReportOne,GPMathContestReport
from reports.models import Reports
from .reportlist import reportlist
from .contacts import contacts
from common.utils import send_sms

def send_link():
    print('start')
    frequency_str = '1,16,17'
    r_type = 'gp_contest_report'
    params = {'gp_name': 'agalakera', 'academic_year': '2017-2018'}

    frequency = frequency_str.split(',')
    today = datetime.datetime.now().strftime("%d")

    for d in frequency:
        if d==today:
            r = reportlist[r_type]
            report = r()
            report.params = params
            result = report.save()
            
            for person in contacts:
                link = report.save_link(result)
                sms = report.get_sms(link.track_id,person['name'])
                # send_sms(num,sms)
                print(person['number'],sms)
                
        
