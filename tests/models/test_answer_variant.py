import pytest

from tests.factories.answer_factory import AnswerVariantFactory


@pytest.mark.django_db
class TestAnswerVariantModel:

    def test_create_answer_variant(self):
        variant = AnswerVariantFactory()
        assert variant.text
        assert variant.question is not None

    def test_is_correct_flag(self):
        correct = AnswerVariantFactory(is_correct=True)
        incorrect = AnswerVariantFactory(is_correct=False)

        assert correct.is_correct is True
        assert incorrect.is_correct is False

    def test_ordering(self):
        question = AnswerVariantFactory().question
        v1 = AnswerVariantFactory(question=question, order=2)
        v2 = AnswerVariantFactory(question=question, order=1)

        variants = list(question.answer_variants.all())
        assert variants[0].order <= variants[1].order
        assert v1.order == 2
        assert v2.order == 1

    def test_str_method(self):
        variant = AnswerVariantFactory(text="Paris", is_correct=True)
        assert "Paris" in str(variant)
        assert "✓" in str(variant) if variant.is_correct else "✓" not in str(variant)

    def test_relationship_with_question(self):
        variant = AnswerVariantFactory()
        assert variant in variant.question.answer_variants.all()
        assert variant.question is not None
