import datetime
import requests
import json

from django.utils import timezone
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import HttpResponse

# Try importing Exotel settings
try:
    EXOTEL_SID = settings.EXOTEL_SID
    EXOTEL_TOKEN = settings.EXOTEL_TOKEN
    EXOTEL_SENDER_ID = settings.EXOTEL_SENDER_ID
except Exception as e:
    # This will obvisouly fail during exotel call
    EXOTEL_SID = 'sid'
    EXOTEL_TOKEN = 'token'
    EXOTEL_SENDER_ID = 'senderid'
finally:
    EXOTEL_URL = 'https://%s:%s@api.exotel.com/v1/Accounts/%s/Sms/send' % (
        EXOTEL_SID, EXOTEL_TOKEN, EXOTEL_SID, )


class Date(object):
    """
    A class with helper functions for checking and retrieving datetime objects.
    """

    def get_datetime(self, date):
        return datetime.datetime.strptime(date, '%Y-%m-%d')

    def check_date_sanity(self, date):
        try:
            year = date.split("-")[0]
            month = date.split("-")[1]
            day = date.split("-")[2]
        except Exception as e:
            return False

        if not self.is_day_correct(day):
            return False

        if not self.is_month_correct(month):
            return False

        if not self.is_year_correct(year):
            return False

        return True

    def is_day_correct(self, day):
        return int(day) in range(1, 32)

    def is_month_correct(self, month):
        return int(month) in range(1, 13)

    def is_year_correct(self, year):
        return (len(year) == 4 and int(year) <= timezone.now().year)


def send_templated_mail(
        from_email, to_emails, subject, template_name, context=None):
    """ Sends html/text email with content rendered from a template """
    plaintext = get_template('email_templates/{}.txt'.format(template_name))
    html = get_template('email_templates/{}.html'.format(template_name))
    text_content = plaintext.render(context)
    html_content = html.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_attachment(from_email, to_emails, subject, folder, filename, context=None):
    msg = EmailMultiAlternatives(subject, "Please view attachment", from_email, to_emails)
    msg.attach_alternative("<b>Please View attachement</b>", "text/html")
    msg.attach_file(os.path.join(settings.PDF_REPORTS_DIR, folder + '/')+filename+".pdf")
    msg.send()


def send_sms(to, msg):
    """ Send a SMS using Exotel API """
    print("Sending SMS using Exotel API")
    data = {
        'From': EXOTEL_SENDER_ID,
        'To': to,
        'Body': msg
    }
    requests.post(EXOTEL_URL, data)


def post_to_slack(channel=None, author=None, message=None, emoji=':ghost:'):
    payload = {
        'text': message,
        'channel': channel,
        'username': author,
        'icon_emoji': emoji
    }

    r = requests.post(
        'https://hooks.slack.com/services/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',
        data=json.dumps(payload),
    )

    return r.status_code
