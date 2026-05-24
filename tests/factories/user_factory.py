import factory
from django.contrib.auth import get_user_model
from factory import fuzzy
from factory.django import DjangoModelFactory

User = get_user_model()


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    role = fuzzy.FuzzyChoice(["organizer", "participant"])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        if "password" not in kwargs:
            kwargs["password"] = "testpass123"
        return manager.create(*args, **kwargs)
