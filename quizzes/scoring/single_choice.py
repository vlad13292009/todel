from .base import BaseScoringStrategy


class SingleChoiceStrategy(BaseScoringStrategy):
    def calculate(self, question, user_answer, max_score):
        correct = question.answer_variants.filter(is_correct=True).first()
        if correct and str(user_answer) == str(correct.id):
            return max_score
        return 0
