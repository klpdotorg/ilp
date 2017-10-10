from django.db.models import Count

from assessments.models import (
    Survey, QuestionGroup, Question
)


class GPContest(object):

    def __init__(self):
        self.class_questiongroup_version_mapping = {
            '4': 1,
            '5': 2,
            '6': 3
        }
        self.survey = Survey.objects.get(name="GP Contest")
        self.questiongroups = self.survey.questiongroup_set.all()       

    def generate_report(self, ans_grp_insti_qs):
        response = {}
        response['summary'] = self.get_meta_summary(ans_grp_insti_qs)
        # classes = ['4', '5', '6']
        # for class_std in classes:
        #     response[class_std] = self.get_classwise_summary(
        #         class_std, ans_grp_insti_qs
        #     )

        return response

    def get_meta_summary(self, ans_grp_insti_qs):
        counts = ans_grp_insti_qs.aggregate(
            school_count=Count('institution', distinct=True),
            gp_count=Count('institution__gp', distinct=True)
        )

        return {
            'schools': counts['school_count'],
            'gps': counts['gp_count'],
            'contests': counts['gp_count']
        }

    def get_classwise_summary(self, class_std, stories):
        class_stories = stories.filter(answer__text=class_std)
        
        male_stories = class_stories.filter(answer__text="Male")
        female_stories = class_stories.filter(answer__text="Female")

        number_of_males = male_stories.count()
        number_of_females = female_stories.count()

        # Gets the number of rows having 20 "Yes"s - Meaning that they
        # answered every question correctly.
        males_with_perfect_score = male_stories.filter(
            answer__text="Yes"
        ).annotate(yes_count=Count('answer')).filter(yes_count=20).count()

        females_with_perfect_score = female_stories.filter(
            answer__text="Yes"
        ).annotate(yes_count=Count('answer')).filter(yes_count=20).count()

        answers = Answer.objects.filter(story__in=class_stories)
        answer_counts = answers.values('question', 'text').annotate(Count('text'))

        competencies = {}

        for entry in answer_counts:
            question = Question.objects.get(id=entry['question'])
            question_text = question.text
            answer_text = entry['text']
            answer_count = entry['text__count']
            if question_text not in competencies:
                competencies[question_text] = {}
            competencies[question_text][answer_text] = answer_count

        return {
            'males':number_of_males,
            'females':number_of_females,
            'males_score':males_with_perfect_score,
            'females_score':females_with_perfect_score,
            'competancies':competencies
        }
