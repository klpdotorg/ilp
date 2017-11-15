from django.db.models import Count

from assessments.models import (
    Survey, Question, AnswerStudentGroup
)


class GPContest(object):

    def __init__(self):
        self.class_qgroup_version_mapping = {
            '4': 1,
            '5': 2,
            '6': 3
        }
        self.survey = Survey.objects.get(name="GP Contest")
        self.questiongroups = self.survey.questiongroup_set.all()

    def generate_report(self, agroup_inst_ids, agroup_studgroup_ids):
        response = {}
        response['summary'] = self.get_meta_summary(
            agroup_inst_ids, agroup_studgroup_ids)
        classes = ['4', '5', '6']
        for class_std in classes:
            response[class_std] = self.get_classwise_summary(
                class_std, agroup_studgroup_ids
            )

        return response

    def get_meta_summary(self, agroup_inst_ids, agroup_studgroup_ids):
        inst_counts = agroup_inst_ids.aggregate(
            school_count=Count('institution', distinct=True),
            gp_count=Count('institution__gp', distinct=True)
        )
        stud_counts = agroup_studgroup_ids.aggregate(
            student_count=Count('studentgroup__students', distinct=True)
        )
        return {
            'schools': inst_counts['school_count'],
            'students': stud_counts['student_count'],
            'gps': inst_counts['gp_count'],
            'contests': inst_counts['gp_count']
        }

    def get_classwise_summary(self, class_std, agroup_studgroup_ids):
        class_stories = agroup_studgroup_ids.filter(
            answerstudentgroup__answer=class_std)

        male_stories = agroup_studgroup_ids.filter(
            answerstudentgroup__answer="Male")
        female_stories = agroup_studgroup_ids.filter(
            answerstudentgroup__answer="Female")

        number_of_males = male_stories.count()
        number_of_females = female_stories.count()

        # Gets the number of rows having 20 "Yes"s - Meaning that they
        # answered every question correctly.
        males_with_perfect_score = male_stories.filter(
            answerstudentgroup__answer="Yes"
        ).annotate(yes_count=Count('answerstudentgroup__answer'))\
            .filter(yes_count=20).count()

        females_with_perfect_score = female_stories.filter(
            answerstudentgroup__answer="Yes"
        ).annotate(yes_count=Count('answerstudentgroup__answer'))\
            .filter(yes_count=20).count()

        answers = AnswerStudentGroup.objects.filter(
            answergroup__in=class_stories)
        answer_counts = answers.values(
            'question', 'answer').annotate(Count('answer'))

        competencies = {}

        for entry in answer_counts:
            question = Question.objects.get(id=entry['question_id'])
            question_text = question.display_text
            answer_text = entry['answer']
            answer_count = entry['answer__count']
            if question_text not in competencies:
                competencies[question_text] = {}
            competencies[question_text][answer_text] = answer_count

        return {
            'males': number_of_males,
            'females': number_of_females,
            'males_score': males_with_perfect_score,
            'females_score': females_with_perfect_score,
            'competancies': competencies
        }
