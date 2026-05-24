import pytest
from django.core.exceptions import ValidationError

from tests.factories.answer_factory import AnswerVariantFactory
from tests.factories.question_factory import QuestionFactory


@pytest.mark.django_db
class TestQuestionModel:

    def test_create_question(self):
        question = QuestionFactory()
        assert question.text
        assert question.question_type in ["single", "multiple", "text", "matching"]
        assert question.points >= 1

    def test_question_type_choices(self):
        for q_type in ["single", "multiple", "text", "matching"]:
            question = QuestionFactory(question_type=q_type)
            assert question.question_type == q_type

    def test_invalid_question_type(self):
        question = QuestionFactory.build(question_type="invalid_type")
        with pytest.raises(ValidationError):
            question.full_clean()

    def test_min_variants_validation(self):
        question = QuestionFactory()
        with pytest.raises(ValidationError):
            question.full_clean()

    def test_at_least_one_correct_answer(self):
        question = QuestionFactory()
        AnswerVariantFactory(question=question, is_correct=False)
        AnswerVariantFactory(question=question, is_correct=False)

        with pytest.raises(ValidationError):
            question.full_clean()

    def test_single_choice_only_one_correct(self):
        question = QuestionFactory(question_type="single")
        AnswerVariantFactory(question=question, is_correct=True)
        AnswerVariantFactory(question=question, is_correct=True)

        with pytest.raises(ValidationError):
            question.full_clean()

    def test_ordering(self):
        quiz = QuestionFactory().quiz
        q1 = QuestionFactory(quiz=quiz, order=2)
        q2 = QuestionFactory(quiz=quiz, order=1)

        questions = list(quiz.questions.all())
        assert questions[0].order <= questions[1].order
        assert q1.order == 2
        assert q2.order == 1

    def test_str_method(self):
        question = QuestionFactory(text="What is 2+2?")
        assert str(question) == "What is 2+2?"[:50]
