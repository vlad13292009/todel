from .base import BaseScoringStrategy


class MatchingStrategy(BaseScoringStrategy):
    def calculate(self, question, user_matches, max_score):
        if not user_matches:
            return 0.0

        all_variants = question.answer_variants.all()
        correct_matches = {}
        left_variants = []

        for variant in all_variants:
            if not variant.is_correct:
                left_variants.append(variant)
                if variant.correct_match_id:
                    correct_matches[variant.id] = variant.correct_match_id
                else:
                    right_variant = all_variants.filter(
                        order=variant.order,
                        is_correct=True
                    ).first()
                    if right_variant:
                        correct_matches[variant.id] = right_variant.id
        if not correct_matches and hasattr(question, 'correct_matches') and question.correct_matches:
            correct_matches = question.correct_matches

        total_pairs = len(correct_matches)
        if total_pairs == 0:
            return 0.0

        correct_count = 0
        for left_id, right_id in user_matches.items():
            left_id = int(left_id) if isinstance(left_id, str) else left_id
            right_id = int(right_id) if isinstance(right_id, str) else right_id

            if left_id in correct_matches and correct_matches[left_id] == right_id:
                correct_count += 1

        score_percentage = correct_count / total_pairs
        return max_score * score_percentage
