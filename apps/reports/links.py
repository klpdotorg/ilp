import datetime

from reports.reports import ReportOne,GPMathContestReport
from reports.models import Reports
from .reportlist import reportlist
from common.utils import send_sms

def send_link():
    frequency_str = '1,16,18'
    r_type = 'gp_contest_report'
    params = {'gp_name': 'agalakera', 'academic_year': '2017-2018'}
    to_numbers = ['917025585877','919037384414']

    frequency = frequency_str.split(',')
    today = datetime.datetime.now().strftime("%d")

    for d in frequency:
        if d==today:
            r = reportlist[r_type]
            report = r()
            report.params = params
            result = report.save()
            
            for num in to_numbers:
                link = report.save_link(result)
                sms = report.get_sms(link.track_id)
                # send_sms(num,sms)
                print(num,sms)
                
        
