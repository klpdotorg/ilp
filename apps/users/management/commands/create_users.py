import csv
from django.core.management.base import BaseCommand
from users.models import User
from common.models import Status, RespondentType


class Command(BaseCommand):

    fileoptions = {"users"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('users')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f)
        return True

    def check_value(self, value, default=None):
        if value.strip() == '':
            if default:
                return default
            return None
        return value

         
    def create_users(self):
        print("here")
        count = 0
        for row in self.csv_files["users"]:
            if count == 0:
                count += 1
                continue
            count += 1

            firstname = row[0].strip()
            lastname = row[1].strip()
            usertype = RespondentType.objects.get(char_id=row[2].strip())
            print(usertype)
            mobile_no = row[3].strip()
            email = row[4].strip()
            is_staff = row[5].strip()
            password = '12345678'
            user = User.objects.create(
                            first_name=firstname,
                            last_name=lastname,
                            mobile_no=mobile_no,
                            password=password,
                            email=email,
                            user_type=usertype,
                            is_active=True,
                            is_mobile_verified=True,
                            is_email_verified=True,
                            opted_email=False,
                            is_staff=is_staff,
                            is_superuser=False)
            print(user)


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
            return

        self.create_users()
