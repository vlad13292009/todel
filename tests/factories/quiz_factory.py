import factory

from quizzes.models import Quiz
from tests.factories.user_factory import CustomUserFactory


class QuizFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Quiz

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    creator = factory.SubFactory(CustomUserFactory, role="organizer")
    status = "draft"
