import factory
from factory import fuzzy

from quizzes.models import AnswerVariant
from tests.factories.question_factory import QuestionFactory


class AnswerVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnswerVariant

    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker("sentence")
    is_correct = fuzzy.FuzzyChoice([True, False])
    order = factory.Sequence(lambda n: n)
