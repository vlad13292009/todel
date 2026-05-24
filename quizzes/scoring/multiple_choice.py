from .base import BaseScoringStrategy


class MultipleChoiceStrategy(BaseScoringStrategy):
    def calculate(self, question, user_answers, max_score):
        correct_ids = set(question.answer_variants.filter(is_correct=True).values_list('id', flat=True))
        selected_ids = set(user_answers)
        correct_count = len(selected_ids & correct_ids)
        total_correct = len(correct_ids)
        if total_correct == 0:
            return 0
        return max_score * (correct_count / total_correct)
