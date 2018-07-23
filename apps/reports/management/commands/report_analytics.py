from django.core.management.base import BaseCommand
from reports.models import Tracking


class Command(BaseCommand):
    help = 'Simple analytices for reports data'

    def handle(self, *args, **options):
        TRACKING = Tracking.objects.all()

        if 'from' in options and 'to' in options:
            TRACKING = TRACKING.filter(
                created_at__range=[options['from'], options['to']]
            )

        # Total reports
        print('Reports created:', round(TRACKING.count()))

        # Report types
        print('\nReport Types:')
        print('DistrictReport', TRACKING.filter(
            report_type__contains='DistrictReport').count()
        )
        print('BlockReport', TRACKING.filter(
            report_type__contains='BlockReport').count()
        )
        print('ClusterReport', TRACKING.filter(
            report_type__contains='ClusterReport').count()
        )
        print('SchoolReport', TRACKING.filter(
            report_type__contains='SchoolReport').count()
        )

        # User types
        print('\nUser Types:')
        user_types = TRACKING.values_list('role').distinct()
        for user in user_types:
            print(user[0], TRACKING.filter(role=user[0]).count())
