import datetime
import csv
import sys


from reports.reports import ReportOne,GPMathContestReport, SchoolReport, ClusterReport, BlockReport, DistrictReport
from reports.models import Reports
from .reportlist import reportlist, param_ids
from .contacts import contacts
from common.utils import send_sms

def send_link_scheduled(dry, filepath, gp_name,arg_two, r_type):
    print(r_type)
   
    frequency_str = '1,16,17,18,04,30'
    if r_type == "ClusterReport":
        params =  {param_ids[r_type]: gp_name,'block_name':arg_two, 'academic_year': '2017-2018'}
    else:
        params = {param_ids[r_type]: gp_name, 'academic_year': '2017-2018'}
    print(params)
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
                    sms = report.get_sms(link.track_id,person[0],param_ids[r_type])
                    if(dry):
                        print('send sms to {}, phone: {}'.format(person[0],person[1]))
                    else:
                        print(person[1],sms)
                        # send_sms(person[1],sms)
    if report_status:
        print("No reports scheduled today")

def send_link(report_type, params, args, dry_run=False):
    if not dry_run:
        report = reportlist[report_type]
        r = report(**params)
        r.get_data()
        result = report.save()
        link = report.save_link(result)
        link.report_type = ''
        link.recipient = args['name']
        link.save()
        sms = report.get_sms(link, args['name'])
        send_sms(args['number'], sms)
    else:
        print("sending {} with arguments {} to {}".format(report_type, params, args['name']))
        
