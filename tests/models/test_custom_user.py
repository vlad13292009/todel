import pytest
from django.db.utils import IntegrityError

from tests.factories.user_factory import CustomUserFactory


@pytest.mark.django_db
class TestCustomUserModel:

    def test_create_organizer(self):
        user = CustomUserFactory(role="organizer")
        assert user.role == "organizer"
        assert user.is_active is True

    def test_create_participant(self):
        user = CustomUserFactory(role="participant")
        assert user.role == "participant"

    def test_email_validation(self):
        user = CustomUserFactory(email="test@example.com")
        assert user.email == "test@example.com"

        with pytest.raises(IntegrityError):
            CustomUserFactory(email="test@example.com")

    def test_username_uniqueness(self):
        CustomUserFactory(username="unique_user")
        with pytest.raises(IntegrityError):
            CustomUserFactory(username="unique_user")

    def test_password_hashing(self):
        user = CustomUserFactory()
        assert user.check_password("testpass123")
        assert user.password != "testpass123"
