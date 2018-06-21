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
        result = r.save()
        link = r.save_link(result)
        link.report_type = '{} for {} between {} and {}'.format(report_type, params[report.parameters[0]], params['report_from'], params['report_to'])
        link.recipient = args['name']
        link.role = args['role']
        link.save()
        sms = r.get_sms(link, args['name'])
        send_sms(args['number'], sms)
    else:
        return "sending {} with arguments {} to {}".format(report_type, params, args['name'])
        
def send_recipient(report_type, report_from, report_to, reader, dry):
    
    is_head_set = False
    head = []
    params = dict(report_from=report_from, report_to=report_to)
    
    messages = []
    successfull = 0
    for person in reader:
            if not is_head_set:
                head = person
                is_head_set = True
            else:
                if getValue(person, head,'First Name') and getValue(person, head,'Mobile Number'):
                    arg = {'name': getValue(person, head,'First Name'),
                           'number':getValue(person, head,'Mobile Number'),
                           'role':getValue(person, head,'role'),
                    }
                    if dry:
                        messages.append("{} is send to {} ,in this number {}".format(report_type, arg['name'], arg['number']))
                        print("{} is send to {} ,in this number {}".format(report_type, arg['name'], arg['number']))
                    else:
                        try:
                            for i in reportlist[report_type].parameters:
                                params[i] = getValue(person, head,i)
                        except ValueError:
                            messages.append("Field {} required for {} not found in csv file".format(i, report_type))
                            print("Field {} required for {} not found in csv file".format(i, report_type))
                            break
                        try:
                            send_link(report_type,params, arg, dry_run=dry)
                            successfull += 1
                            messages.append("{} is send to {} ,in this number {}".format(report_type, arg['name'], arg['number']))
                            print("{} is send to {} ,in this number {}".format(report_type, arg['name'], arg['number'])))
                        except ValueError as e:
                            messages.append(e.args[0])
                            print(e.args[0])
    return messages
        
def getValue( person, head, i):
    index = head.index(i)
    value = person[index]
    return value
