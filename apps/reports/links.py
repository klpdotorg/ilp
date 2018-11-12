from .reportlist import reportlist
from common.utils import send_sms


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
        print(args['number'], sms)
        # send_sms(args['number'], sms)
    else:
        return "sending {} with arguments {} to {}".format(report_type, params, args['name'])

        
def send_recipient(report_type, report_from, report_to, reader, dry, start_from, gka, gp, hhsurvey, quit_on_error = False):
    # is_head_set = False
    # head = []
    params = dict(report_from=report_from, report_to=report_to, generate_gka = gka, generate_gp = gp, generate_hhsurvey = hhsurvey)
    messages = []
    successfull = 0
    head = next(reader)
    en_reader = enumerate(reader)

    if start_from:
        for i in range(start_from):
            print ("Skipping {}".format(next(en_reader)[1]))

    for line_no,person in en_reader:
        if get_value(person, head,'First Name') and get_value(person, head,'Mobile Number'):
            arg = {'name': get_value(person, head,'First Name'),
                   'number':get_value(person, head,'Mobile Number'),
                   'role':get_value(person, head,'role'),
            }
            if dry:
                messages.append("{} will be sent to {} ({})".format(report_type, arg['name'], arg['number']))
                successfull += 1
            else:
                try:
                    for i in reportlist[report_type].parameters:
                        params[i] = get_value(person, head,i)
                    send_link(report_type,params, arg, dry_run=dry)
                    successfull += 1
                    messages.append("{} has been sent to {} ({})".format(report_type, arg['name'], arg['number']))
                except Exception as e:
                    print(e)
                    messages.append(e.args[0])
                    if quit_on_error:
                        print("Error on line {}. Use --skip parameter with this value to continue.".format(line_no))
                        break
                    else:
                        print("Error on line {} - {}.".format(line_no, e))
    return dict(messages=messages, successfull=successfull)
        
def get_value(person, head, i):
    index = head.index(i)
    value = person[index]
    return value
