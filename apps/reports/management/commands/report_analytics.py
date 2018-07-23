from django.core.management.base import BaseCommand
from reports.models import Tracking


REPORT_TYPES = [
    'DistrictReport',
    'BlockReport',
    'ClusterReport',
    'SchoolReport',
]


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
        for report_type in REPORT_TYPES:
            print(report_type, TRACKING.filter(
                report_type__contains=report_type).count()
            )

        # User types
        print('\nUser Types:')
        user_types = TRACKING.values_list('role').distinct()
        for user in user_types:
            print(user[0], TRACKING.filter(role=user[0]).count())

        # Total views and downloads
        print('\nViews and Downloads')
        for report_type in REPORT_TYPES:
            t = TRACKING.filter(report_type__contains=report_type)
            print(
                report_type,
                'Views', t.exclude(visited_at=None).count(),
                'Downloads', t.exclude(downloaded_at=None).count()
            )
