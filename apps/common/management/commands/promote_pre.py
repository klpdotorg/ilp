import csv
import sys
from io import StringIO

from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from schools.models import StudentStudentGroupRelation, StudentGroup, Student
from common.models import Status, AcademicYear
from datetime import date
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):

    today = date.today()
    po_status = Status.objects.get(char_id='PO')
    inactive_status = Status.objects.get(char_id='IA')
    active_status = Status.objects.get(char_id='AC')
   
    def add_arguments(self, parser):
        parser.add_argument('new_academic_year')

    def set_new_year_entry(self, student_year, new_academic_year):
        studentgroup = StudentGroup.objects.get(id=student_year.student_group.id)
        student = Student.objects.get(id=student_year.student_id)
        try:
            studentyear = StudentStudentGroupRelation.objects.get_or_create(student=student,
                student_group = studentgroup, academic_year = new_academic_year,
                status=self.active_status)
        except IntegrityError:
            print("Entry already exists")
        
    def set_po_new_year_entry(self, student_year, new_academic_year):
        student = Student.objects.get(id=student_year.student_id)
        student_group = StudentGroup.objects.get(id=student_year.student_group.id)
        studentyear = StudentStudentGroupRelation.objects.get_or_create(student=student,
            student_group = student_group, academic_year = new_academic_year,
            status=self.po_status)

    def update_current_year_status(self, student_year_list):
        student_year_list.update(status_id=self.inactive_status)
        
    def promote_students(self, new_academic_year, current_academic_year,current_year):
            valid_birthday_start = date(current_year - 6, 6, 1)
            print(valid_birthday_start)
            student_active_year_list = StudentStudentGroupRelation.objects.filter(
                academic_year_id=current_academic_year,
	        student_id__institution_id__institution_type_id='pre', status_id='AC',
                student_id__dob__gte = valid_birthday_start)
            print(student_active_year_list.count())
            for student_year in student_active_year_list:
                self.set_new_year_entry(student_year, new_academic_year)
            self.update_current_year_status(student_active_year_list)

            student_po_year_list = StudentStudentGroupRelation.objects.filter(
                academic_year_id=current_academic_year,
	        student_id__institution_id__institution_type_id='pre', status_id='AC',
                student_id__dob__lt = valid_birthday_start)
            print(student_po_year_list.count())
            for student_po_year in student_po_year_list:
                self.set_po_new_year_entry(student_po_year, new_academic_year)
            self.update_current_year_status(student_po_year_list)

    def handle(self, *args, **options):

        new_academic_year = options['new_academic_year']
        current_academic_year = settings.DEFAULT_ACADEMIC_YEAR
        expected_academic_year = current_academic_year[2:4] + str(int(current_academic_year[2:4])+1)
        current_year = int('20'+current_academic_year[2:4])
        if new_academic_year != expected_academic_year:
            print("Check the academic year, current year is : "+current_academic_year+", Expected :"+expected_academic_year)
            return
        new_ac_year = AcademicYear.objects.get(char_id=new_academic_year)
        self.promote_students(new_ac_year, current_academic_year,current_year) 
