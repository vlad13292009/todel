from .matching import MatchingStrategy
from .multiple_choice import MultipleChoiceStrategy
from .single_choice import SingleChoiceStrategy
from .text_answer import TextAnswerStrategy


class ScoringFactory:
    _strategies = {
        "single": SingleChoiceStrategy(),
        "multiple": MultipleChoiceStrategy(),
        "text": TextAnswerStrategy(),
        "matching": MatchingStrategy(),
    }

    @classmethod
    def get_strategy(cls, question_type):
        if question_type not in cls._strategies:
            raise ValueError(f"Unknown question type: {question_type}")
        return cls._strategies[question_type]
