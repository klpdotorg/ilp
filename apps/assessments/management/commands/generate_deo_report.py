from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from easyaudit.models import CRUDEvent
from users.models import User


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--from',
            help='From date'
        )
        parser.add_argument(
            '-t', '--to',
            help='To date'
        )

    def convert_to_date(self, date_string):
        if not date_string:
            return None
        year, month, day = date_string.split("-")
        return date(int(year), int(month), int(day))

    def handle(self, *args, **options):
        model_names = [
            'student', 'studentgroup', 'institution',
            'answergroup_student', 'answergroup_studentgroup',
            'answergroup_institution',
            'answerstudent', 'answerstudentgroup', 'answerinstitution'
        ]
        actions = [1, 2, 3]
        from_ = self.convert_to_date(options['from'])
        to_ = self.convert_to_date(options['to'])
        events = CRUDEvent.objects.all()
        if from_:
            events = events.filter(datetime__gte=from_)
        if to_:
            events = events.filter(datetime__lte=to_)
        
        user_ids = events.order_by().\
            distinct('user_id').values_list('user_id', flat=True)

        with open('deo-report.csv', 'w') as csvfile:
            csvfile.write(
                ("sl_no, user, user_name, "
                "student-create, student-update, student-delete,"
                "studentgroup-create, studengroup-update, studengroup-delete,"
                "institution-create, institution-update, institution-delete,"
                "answergroup_student-create, answergroup_student-update, answergroup_student-delete,"
                "answergroup_studentgroup-create, answergroup_studengroup-update, answergroup_studengroup-delete,"
                "answergroup_institution-create, answergroup_institution-update, answergroup_institution-delete,"
                "answer_student-create, answer_student-update, answer_student-delete,"
                "answer_studentgroup-create, answer_studengroup-update, answer_studengroup-delete,"
                "answer_institution-create, answer_institution-update, answer_institution-delete \n")
            )
            for sl_no, user in enumerate(user_ids):
                user_name = User.objects.get(id=user).get_full_name()
                csvfile.write(str(sl_no)+","+str(user)+","+str(user_name)+",")
                for model_name in model_names:
                    content_type = ContentType.objects.get(model=model_name)
                    for action in actions:
                        events = CRUDEvent.objects.filter(
                            user_id=user, content_type=content_type,
                            event_type=action
                        )
                        if from_:
                            events = events.filter(datetime__gte=from_)
                        if to_:
                            events = events.filter(datetime__lte=to_)
                        csvfile.write(str(events.count())+",")
                csvfile.write('\n')
        csvfile.close()
