import sqlite3
from datetime import datetime

from django.core.management.base import BaseCommand

from assessments.models import (
    QuestionGroup,
    AnswerGroup_Institution,
    AnswerInstitution
)

YES_NO = {
    'Yes': 1,
    'No': 0
}
connection = sqlite3.connect('klp.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE classes ( "index" BIGINT, "Block" TEXT, "Date" TEXT, "District" TEXT, "Government School -1 / Private School - 2" TEXT, "Grama Panchayat" TEXT, "KLP ID" BIGINT, "Name of the school" TEXT, "Q1" BIGINT, "Q10" BIGINT, "Q11" BIGINT, "Q12" BIGINT, "Q13" BIGINT, "Q14" BIGINT, "Q15" BIGINT, "Q16" BIGINT, "Q17" BIGINT, "Q18" BIGINT, "Q19" BIGINT, "Q2" BIGINT, "Q20" BIGINT, "Q3" BIGINT, "Q4" BIGINT, "Q5" BIGINT, "Q6" BIGINT, "Q7" BIGINT, "Q8" BIGINT, "Q9" BIGINT, "Sex ( Male / Female )" TEXT, "Total" BIGINT, "Village" TEXT, class BIGINT )')
connection.commit()
cursor.execute('CREATE INDEX ix_classes_index ON classes ("index")')
connection.commit()

class Command(BaseCommand):
    help = 'Generates data in sqlite form to be fed to superset dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--from',
            help='From date'
        )
        parser.add_argument(
            '-t', '--to',
            help='To date'
        )

    def handle(self, *args, **options):
        # Get question groups for GP Contest
        question_groups = QuestionGroup.objects.filter(survey__id=2).values_list('id', flat=True)
        # Get assessments done for those question groups
        answer_group = AnswerGroup_Institution.objects.filter(
            questiongroup__id__in=question_groups
        ).order_by('-pk')

        # If from and to are passed from the command line, filter data in those date ranges
        if options['from'] is not None and options['to'] is not None:
            from_date = datetime.strptime(options['from'], '%Y-%m-%d')
            to_date = datetime.strptime(options['to'], '%Y-%m-%d')
            answer_group = answer_group.filter(
                entered_at__range=[from_date, to_date]
            )

        i = 1
        total = answer_group.count()

        for ag in answer_group:
            answers = AnswerInstitution.objects.filter(answergroup=ag).exclude(
                question__question_text__in=['Gender', 'Class visited']
            )
            other_answers = AnswerInstitution.objects.filter(
                answergroup=ag,
                question__question_text='Gender'
            )

            # Safety checks
            if answers.count() != 20 or other_answers.count() != 1:
                print('Error on ', ag.id)
                i += 1
                continue

            data = {
                'index': i - 1,
                "Block": ag.institution.admin2.name,
                "Date": ag.entered_at,
                "District": ag.institution.admin1.name,
                "Government School -1 / Private School - 2": 1,
                "Grama Panchayat": ag.institution.gp.const_ward_name,
                "KLP ID": ag.institution.id,
                "Name of the school": ag.institution.name,
                "Q1": YES_NO[answers[0].answer],
                "Q2": YES_NO[answers[1].answer],
                "Q3": YES_NO[answers[2].answer],
                "Q4": YES_NO[answers[3].answer],
                "Q5": YES_NO[answers[4].answer],
                "Q6": YES_NO[answers[5].answer],
                "Q7": YES_NO[answers[6].answer],
                "Q8": YES_NO[answers[7].answer],
                "Q9": YES_NO[answers[8].answer],
                "Q10": YES_NO[answers[9].answer],
                "Q11": YES_NO[answers[10].answer],
                "Q12": YES_NO[answers[11].answer],
                "Q13": YES_NO[answers[12].answer],
                "Q14": YES_NO[answers[13].answer],
                "Q15": YES_NO[answers[14].answer],
                "Q16": YES_NO[answers[15].answer],
                "Q17": YES_NO[answers[16].answer],
                "Q18": YES_NO[answers[17].answer],
                "Q19": YES_NO[answers[18].answer],
                "Q20": YES_NO[answers[19].answer],
                "Sex ( Male / Female )": other_answers[0].answer,
                "Total": 0,
                "Village": ag.institution.gp.const_ward_name,
                "class": ag.questiongroup.name.split(' ')[1],
            }
            # Collect all data needed to insert one row in the classes table

            # Calculate total as sum of all Yes and Nos
            for ans in answers:
                    data['Total'] += YES_NO[ans.answer]

            # Finally save data to Sqlite
            connection.execute(
                'insert into classes values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                [
                    data['index'],
                    data["Block"],
                    data["Date"],
                    data["District"],
                    data["Government School -1 / Private School - 2"],
                    data["Grama Panchayat"],
                    data["KLP ID"],
                    data["Name of the school"],
                    data["Q1"],
                    data["Q2"],
                    data["Q3"],
                    data["Q4"],
                    data["Q5"],
                    data["Q6"],
                    data["Q7"],
                    data["Q8"],
                    data["Q9"],
                    data["Q10"],
                    data["Q11"],
                    data["Q12"],
                    data["Q13"],
                    data["Q14"],
                    data["Q15"],
                    data["Q16"],
                    data["Q17"],
                    data["Q18"],
                    data["Q19"],
                    data["Q20"],
                    data["Sex ( Male / Female )"],
                    data["Total"],
                    data["Village"],
                    data["class"],
                 ]
            )
            connection.commit()

            print('({0}/{1})'.format(i, total))
            i += 1
