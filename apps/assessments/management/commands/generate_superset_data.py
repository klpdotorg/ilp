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
        connection = sqlite3.connect('klp.db')
        cursor = connection.cursor()

        for ag in answer_group:
            answers = AnswerInstitution.objects.filter(answergroup=ag).order_by(
                'question__key'
            )

            data = {
                'id': None,
                "Sex ( Male / Female )": answers[10].answer,
                "class": ag.questiongroup.name.split(' ')[1],
                "District": ag.institution.admin1.name,
                "Block": ag.institution.admin2.name,
                "Cluster": ag.institution.admin3.name,
                "Date": ag.entered_at,
                "Grama Panchayat": ag.institution.gp.const_ward_name,
                "KLP ID": ag.institution.id,
                "Name of the school": ag.institution.name,
                "Q1": YES_NO[answers[2].answer],
                "Q2": YES_NO[answers[3].answer],
                "Q3": YES_NO[answers[4].answer],
                "Q4": YES_NO[answers[5].answer],
                "Q5": YES_NO[answers[6].answer],
                "Q6": YES_NO[answers[7].answer],
                "Q7": YES_NO[answers[8].answer],
                "Q8": YES_NO[answers[9].answer],
                "Q9": YES_NO[answers[0].answer],
                "Q10": YES_NO[answers[1].answer],
                "Q11": YES_NO[answers[12].answer],
                "Q12": YES_NO[answers[13].answer],
                "Q13": YES_NO[answers[14].answer],
                "Q14": YES_NO[answers[15].answer],
                "Q15": YES_NO[answers[16].answer],
                "Q16": YES_NO[answers[17].answer],
                "Q17": YES_NO[answers[18].answer],
                "Q18": YES_NO[answers[19].answer],
                "Q19": YES_NO[answers[20].answer],
                "Q20": YES_NO[answers[21].answer],
                "Total": 0
            }
            # Collect all data needed to insert one row in the classes table

            # Calculate total as sum of all Yes and Nos
            for ans in answers[2:]:
                if ans.question.question_text not in ['Gender', 'Class visited']:
                    data['Total'] += YES_NO[ans.answer]

            # Finally save data to Sqlite
            connection.execute(
                'insert into classes values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                list(data.values())
            )
            connection.commit()

            print('({0}/{1})'.format(i, total))
            i += 1
