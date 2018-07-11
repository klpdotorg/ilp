from django.core.management.base import BaseCommand
from assessments.models import *
from boundary.models import *


class Command(BaseCommand):
    help = 'Test for reports data'

    def handle(self, *args, **options):
        date_range = ['2017-06-01', '2018-03-31']
        block_name = 'hosakote'
        block = Boundary.objects.get(boundary_type_id='SB', name=block_name)

        # Traditional way
        yes = AnswerGroup_Institution.objects.filter(
            answers__question__question_text__icontains='trained',
            answers__answer='Yes', date_of_visit__range=date_range,
            questiongroup__survey_id=11, institution__admin2=block
        ).count()

        total = AnswerGroup_Institution.objects.filter(
            answers__question__question_text__icontains='trained',
            date_of_visit__range=date_range,
            questiongroup__survey_id=11, institution__admin2=block
        ).count()
        traditional_percentage = round(yes / total * 100, 2)

        print(
            'Traditional way: Teach trained in ',
            block.name,
            block.parent.name,
            'Yes {}'.format(yes), 'Total {}'.format(total),
            'Percentage {}'.format(traditional_percentage)
        )

        # 1 million report way
        clusters  = Boundary.objects.filter(
            parent=block, boundary_type__char_id='SC'
        )
        cluster_gka = []

        for cluster in clusters:
            GKA = AnswerGroup_Institution.objects.filter(
                institution__admin3=cluster,
                date_of_visit__range=date_range,
                questiongroup__survey_id=11
            )
            if GKA.exists():
                teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
                cluster_gka.append(
                    dict(
                        cluster=cluster.name,
                        teachers_trained=round(teachers_trained*100, 2))
                    )
            else:
                print("No GKA data for CLUSTER {} in {} block for academic year {}".format(cluster.name, cluster.parent.name, date_range))
                continue

        if not cluster_gka:
            raise ValueError("No GKA data for '{}' between {} and {}".format(block.name, date_range[0], date_range[1]))

        gka = {
            'teachers_trained': round(
                AnswerGroup_Institution.objects.filter(
                    institution__admin2=block,
                    date_of_visit__range=date_range,
                    questiongroup__survey_id=11,
                    answers__question__question_text__icontains='trained',
                    answers__answer='Yes'
                ).count() / AnswerGroup_Institution.objects.filter(
                    institution__admin2=block,
                    date_of_visit__range=date_range,
                    questiongroup__survey_id=11,
                    answers__question__question_text__icontains='trained'
                ).count() * 100,
                2
            )
        }

        million_percentage = gka['teachers_trained']
        print(
            '1million way: Teach trained in ',
            block.name,
            block.parent.name,
            'Percentage {}'.format(million_percentage)
        )

        if traditional_percentage == million_percentage:
            print('Traditional and 1million way matches')
        else:
            print('Traditional and 1million way does not match')

