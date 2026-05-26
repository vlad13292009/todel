from .base import BaseScoringStrategy


class MatchingStrategy(BaseScoringStrategy):
    def calculate(self, question, user_answer, max_score):
        if not user_answer:
            return 0.0

        all_variants = list(question.answer_variants.all())

        left_variants = [v for v in all_variants if not v.is_correct]
        right_variants = [v for v in all_variants if v.is_correct]

        if len(left_variants) != len(right_variants) or not left_variants:
            return 0.0

        left_variants.sort(key=lambda v: v.order)
        right_variants.sort(key=lambda v: v.order)

        correct_matches = {}
        for left, right in zip(left_variants, right_variants):
            correct_matches[str(left.id)] = right.id

        correct_count = 0
        for left_id, right_id in user_answer.items():
            left_id = str(left_id)
            right_id = int(right_id) if isinstance(right_id, str) else right_id
            if correct_matches.get(left_id) == right_id:
                correct_count += 1

        return round(max_score * (correct_count / len(correct_matches)), 2)
