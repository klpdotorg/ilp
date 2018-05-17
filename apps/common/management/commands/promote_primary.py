import csv
import sys
from io import StringIO

from django.conf import settings
from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from schools.models import StudentStudentGroupRelation, StudentGroup, Student
from common.models import Status, AcademicYear


class Command(BaseCommand):

    po_status = Status.objects.get(char_id='PO')
    inactive_status = Status.objects.get(char_id='IA')
    active_status = Status.objects.get(char_id='AC')
   
    def add_arguments(self, parser):
        parser.add_argument('new_academic_year')
        parser.add_argument('class')

    def set_new_year_entry(self, student_year, new_academic_year, sg):
        new_class = int(sg) + 1
        old_studentgroup = StudentGroup.objects.get(id=student_year.student_group.id)
        new_studentgroup, created = StudentGroup.objects.get_or_create(name=new_class, section=old_studentgroup.section, institution=old_studentgroup.institution,status=self.active_status)
        student = Student.objects.get(id=student_year.student_id)
        try:
            studentyear = StudentStudentGroupRelation.objects.get_or_create(student=student,
                student_group = new_studentgroup, academic_year = new_academic_year,
                status=self.active_status)
        except IntegrityError:
            print("Entry already exists")
        
    def set_po_new_year_entry(self, student_year, new_academic_year):
        student = Student.objects.get(id=student_year.student_id)
        status = self.po_status
        student_group = StudentGroup.objects.get(id=student_year.student_group.id)
        studentyear = StudentStudentGroupRelation.objects.get_or_create(student=student,
            student_group = student_group, academic_year = new_academic_year,
            status=status)
        print(studentyear)

    def update_current_year_status(self, student_year_list):
        student_year_list.update(status_id=self.inactive_status)
        
    def promote_students(self, new_academic_year, current_academic_year, sg):
        if sg == '10':
            #set status for students in class 10 as PO
            student_po_year_list = StudentStudentGroupRelation.objects.filter(
                academic_year_id=current_academic_year,
	        student_id__institution_id__institution_type_id='primary', status_id='AC',
                student_group_id__name = sg)
            print(student_po_year_list.count())
            for student_year in student_po_year_list:
                self.set_po_new_year_entry(student_year, new_academic_year)
            self.update_current_year_status(student_po_year_list)

        else:
            student_year_list = StudentStudentGroupRelation.objects.filter(
                academic_year_id=current_academic_year,
	        student_id__institution_id__institution_type_id='primary', status_id='AC',
                student_group_id__name = sg)
            print(student_year_list.count())
            for student_year in student_year_list:
                self.set_new_year_entry(student_year, new_academic_year,sg)
            self.update_current_year_status(student_year_list)

    def handle(self, *args, **options):

        new_academic_year = options['new_academic_year']
        sg = options['class']
        current_academic_year = settings.DEFAULT_ACADEMIC_YEAR
        expected_academic_year = current_academic_year[2:4] + str(int(current_academic_year[2:4])+1)
        if new_academic_year != expected_academic_year:
            print("Check the academic year, current year is : "+current_academic_year+", Expected :"+expected_academic_year)
            return
        new_ac_year = AcademicYear.objects.get(char_id=new_academic_year)
        self.promote_students(new_ac_year, current_academic_year, sg) 
