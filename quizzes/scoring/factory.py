from .single_choice import SingleChoiceStrategy
from .multiple_choice import MultipleChoiceStrategy
from .text_answer import TextAnswerStrategy
from .matching import MatchingStrategy


class ScoringFactory:
    _strategies = {
        'single': SingleChoiceStrategy(),
        'multiple': MultipleChoiceStrategy(),
        'text': TextAnswerStrategy(),
        'matching': MatchingStrategy(),
    }

    @classmethod
    def get_strategy(cls, question_type):
        if question_type not in cls._strategies:
            raise ValueError(f'Unknown question type: {question_type}')
        return cls._strategies[question_type]
