from abc import ABC, abstractmethod


class BaseScoringStrategy(ABC):
    @abstractmethod
    def calculate(self, question, user_answer, max_score):
        pass
