import pytest
from django.core.exceptions import ValidationError

from tests.factories.question_factory import QuestionFactory
from tests.factories.quiz_factory import QuizFactory


@pytest.mark.django_db
class TestQuizModel:
    def test_create_quiz(self):
        quiz = QuizFactory()
        assert quiz.title
        assert quiz.status == "draft"

    def test_status_choices(self):
        for status in ["draft", "published", "archived"]:
            quiz = QuizFactory(status=status)
            assert quiz.status == status

    def test_invalid_status(self):
        quiz = QuizFactory.build(status="invalid_status")
        with pytest.raises(ValidationError):
            quiz.full_clean()

    def test_title_min_length(self):
        quiz = QuizFactory(title="Ab")
        with pytest.raises(ValidationError):
            quiz.full_clean()

    def test_questions_limit(self):
        quiz = QuizFactory()
        for _ in range(100):
            QuestionFactory(quiz=quiz)

        assert quiz.questions.count() == 100

    def test_creator_relationship(self):
        quiz = QuizFactory()
        assert quiz.creator.is_authenticated
        assert hasattr(quiz.creator, "quizzes")
        assert quiz in quiz.creator.quizzes.all()

    def test_str_method(self):
        quiz = QuizFactory(title="Test Quiz")
        assert str(quiz) == "Test Quiz"
