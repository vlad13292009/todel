from .base import BaseScoringStrategy


class TextAnswerStrategy(BaseScoringStrategy):
    def calculate(self, question, user_answer, max_score):
        correct = question.answer_variants.filter(is_correct=True).first()
        if correct and user_answer.strip().lower() == correct.text.strip().lower():
            return max_score
        return 0
