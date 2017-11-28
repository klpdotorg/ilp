import datetime

from django.utils import timezone
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


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
        except:
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
