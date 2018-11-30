import csv
import sys
from io import StringIO

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from assessments.models import QuestionGroup, Question, QuestionGroup_Questions, Concept, MicroConceptGroup, MicroConcept, QuestionLevel, QuestionInformationType, LearningIndicator
from common.models import Status


class Command(BaseCommand):
   
    fileoptions = {"questiondetails"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiondetails')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print ("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f,delimiter='|')
        return True


    def get_question(self, concept, microconceptgroup, microconcept, questionlevel, questioninformationtype, learningindicator, questiongroup, sequence):
        question = QuestionGroup_Questions.objects.get(questiongroup = questiongroup, sequence=sequence).question
        if question.concept == '' or question.concept == None:
            print("updating")
            question.concept_id = concept.pk
            question.microconcept_group_id = microconceptgroup.pk
            question.microconcept_id = microconcept.pk
            question.question_level_id = questionlevel.pk
            question.question_info_type_id = questioninformationtype.pk
            question.learning_indicator_id = learningindicator.pk
            question.save()
            return question, False 
        else:
            if question.concept == concept and question.microconcept_group == microconceptgroup and question.microconcept == microconcept and question.question_level == questionlevel and question.question_info_type == questioninformationtype and question.learning_indicator == learningindicator:
                print("present")
                return question, False 
            else:
                print("creating question")
                question = Question.objects.create(question_text=microconcept.description, display_text=microconcept.description, is_featured='True',status = Status.objects.get(pk='AC'), concept_id=concept.pk, microconcept_group_id=microconceptgroup.pk, microconcept_id=microconcept.pk, question_level_id=questionlevel.pk, question_info_type_id=questioninformationtype.pk,learning_indicator_id=learningindicator.pk)
                return question, True 
            


    def update_questiondetails(self):
        count=0
        for row in self.csv_files["questiondetails"]:
            if count == 0:
                count += 1
                continue
            count += 1
            questiongroup = QuestionGroup.objects.get(pk = row[0].strip())
            sequence = row[1].strip()
            concept = Concept.objects.get(char_id = row[2].strip())
            microconceptgroup = MicroConceptGroup.objects.get(char_id=row[3].strip())
            microconcept = MicroConcept.objects.get(char_id = row[4].strip())
            questionlevel = QuestionLevel.objects.get(char_id=row[5].strip())
            questioninformationtype = QuestionInformationType.objects.get(char_id=row[6].strip())
            learningindicator = LearningIndicator.objects.get(char_id=row[7].strip())
            question, created = self.get_question(concept, microconceptgroup, microconcept, questionlevel, questioninformationtype, learningindicator, questiongroup, sequence)
         
            if created:
                print("updating questiongroup: "+str(questiongroup.id)+" "+str(sequence))
                qgq = QuestionGroup_Questions.objects.get(questiongroup=questiongroup, sequence=sequence)
                qgq.question = question
                qgq.save()



    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        self.update_questiondetails()
