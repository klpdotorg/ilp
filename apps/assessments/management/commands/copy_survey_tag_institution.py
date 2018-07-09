from django.core.management.base import BaseCommand
from assessments.models import SurveyTagInstitutionMapping


class Command(BaseCommand):
    help = """
        Copy survey institution taggings from one academic year to another
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-g', '--tag',
            help='Tag to attach'
        )
        parser.add_argument(
            '-s', '--source',
            help='Source academic year'
        )
        parser.add_argument(
            '-t', '--target',
            help='Target academic year'
        )

    def copy_institution_tag(self, tag, source, target):
        institutions = SurveyTagInstitutionMapping.objects.filter(
            tag_id=tag,
            academic_year_id=source
        )
        created_count = 0

        for i in institutions:
            created = SurveyTagInstitutionMapping.objects.get_or_create(
                tag_id=tag,
                institution_id=i.institution_id,
                academic_year_id=target
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            'Copied %s institution ids from %s sources' % (
                created_count,
                institutions.count()
            )
        ))

    def handle(self, *args, **options):
            tag = options['tag']
            source = options['source']
            target = options['target']

            if tag is None or source is None or target is None:
                self.stderr.write(self.style.ERROR(
                    'I need tag, source & target to proceed.'
                ))
                exit(1)
            else:
                self.copy_institution_tag(tag, source, target)
