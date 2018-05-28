from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
import io
import re
import os

app_names = {'users', 'common', 'boundary', 'schools', 'dise', 'assessments', 'ivrs'}


class Command(BaseCommand):

    def handle(self, *args, **options):

        for app in app_names:
            output =  io.StringIO()
            call_command('sqlsequencereset', app, stdout=output, no_color=True)
            lines = output.getvalue().splitlines()
            sql = io.StringIO()
            for line in lines:
                line=re.sub(r'^.+mvw.*$','',line)
                if line:
                    sql.write(line+'\n')
            with connection.cursor() as cursor:
                cursor.execute(sql.getvalue())
