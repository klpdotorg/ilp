import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = """Executes

    psql -h HOSTNAME -U USERNAME -d DBNAME -f
        ../../imports/aggregates/materialized_views.sql

    """

    def handle(self, *args, **options):
        dsettings = settings.DATABASES['default']
        dbname = dsettings['NAME']
        print("DB name is: ", dbname)
        command = (
            "psql -h {} -U {} -d {} -f "
            "imports/aggregates/materialized_views.sql".format(
               dsettings['HOST'], dsettings['USER'], dbname
            )
        )
        os.system(command)
