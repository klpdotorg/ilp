import csv
from django.core.management.base import BaseCommand
from assessments.models import Question, QuestionType, QuestionGroup, QuestionGroup_Questions
from common.models import Status


class Command(BaseCommand):

    fileoptions = {"questions"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questions')

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

    def map_questiongroup_question(self, questiongroup, question, sequence):
        count=0
        qgq_map = QuestionGroup_Questions.objects.create(
                      sequence = sequence,
                      question = question,
                      questiongroup = questiongroup)

         
    def create_questions(self):
        count = 0
        questions = []
        for row in self.csv_files["questions"]:
            if count == 0:
                count += 1
                continue
            count += 1

            questiongroup = QuestionGroup.objects.get(id=row[0].strip())
            sequence = row[1]
            question_text = row[2].strip()
            display_text = row[3].strip()
            key = self.check_value(row[4].strip())
            options = self.check_value(row[5].strip())
            is_featured = self.check_value(row[6].strip(), True)
            question_type = QuestionType.objects.get(id=self.check_value(
                                                            row[7].strip(), 4))
            status = Status.objects.get(char_id=row[8].strip())
            max_score = self.check_value(row[9].strip(), 0)
            pass_score = self.check_value(row[10].strip(), 0)
            lang_name = self.check_value(row[11].strip())
            lang_options = self.check_value(row[12].strip())
            question = Question.objects.create(
                            question_text=question_text,
                            display_text=display_text,
                            key=key,
                            options=options,
                            is_featured=is_featured,
                            question_type=question_type,
                            status=status,
                            max_score=max_score,
                            pass_score=pass_score,
                            lang_name=lang_name,
                            lang_options=lang_options)
            self.map_questiongroup_question(questiongroup, question, sequence)



    def handle(self, *args, **options):
        if not self.get_csv_files(options):
            return

        self.create_questions()
