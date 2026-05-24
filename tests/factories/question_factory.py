import factory
from factory import fuzzy

from quizzes.models import Question
from tests.factories.quiz_factory import QuizFactory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    quiz = factory.SubFactory(QuizFactory)
    text = factory.Faker("sentence")
    question_type = factory.fuzzy.FuzzyChoice(
        [
            "single",
            "multiple",
            "text",
            "matching",
        ],
    )
    points = fuzzy.FuzzyInteger(1, 10)
    order = factory.Sequence(lambda n: n)
