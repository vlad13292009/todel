from django.contrib.auth import get_user_model
from django.test import TestCase

from quizzes.models import AnswerVariant, Question, Quiz
from .models import ParticipantAnswer, ParticipantSession, QuizSession

User = get_user_model()


class QuizSessionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="org",
            email="org@testsession.com",
            password="pass12345!",
            role="organizer",
        )
        self.quiz = Quiz.objects.create(
            title="Test Quiz", description="Desc", creator=self.user
        )
        self.question = Question.objects.create(
            quiz=self.quiz, text="Q?", order=1
        )
        self.answer = AnswerVariant.objects.create(
            question=self.question, text="A", is_correct=True, order=1
        )

    def test_quiz_session_creation(self):
        session = QuizSession.objects.create(
            quiz=self.quiz,
            unique_code="ABC123",
            status="waiting",
        )
        self.assertEqual(session.quiz, self.quiz)
        self.assertEqual(session.unique_code, "ABC123")
        self.assertEqual(session.status, "waiting")
        self.assertIsNone(session.started_at)
        self.assertIsNone(session.finished_at)
        self.assertEqual(str(session), f"{self.quiz.title} - ABC123")

    def test_quiz_session_default_status(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="DEF456"
        )
        self.assertEqual(session.status, "waiting")

    def test_participant_session_creation_with_user(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="GHI789"
        )
        participant = User.objects.create_user(
            username="part",
            email="part@testsession.com",
            password="pass12345!",
            role="participant",
        )
        ps = ParticipantSession.objects.create(
            session=session,
            user=participant,
            total_score=10,
            correct_answers_count=2,
        )
        self.assertEqual(ps.session, session)
        self.assertEqual(ps.user, participant)
        self.assertEqual(ps.total_score, 10)
        self.assertEqual(ps.correct_answers_count, 2)
        self.assertIn(participant.username, str(ps))

    def test_participant_session_creation_anonymous(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="JKL012"
        )
        ps = ParticipantSession.objects.create(
            session=session,
            participant_name="Anon",
        )
        self.assertEqual(ps.participant_name, "Anon")
        self.assertIsNone(ps.user)
        self.assertIn("Anon", str(ps))

    def test_participant_answer_creation(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="MNO345"
        )
        ps = ParticipantSession.objects.create(
            session=session,
            participant_name="Player1",
        )
        answer = ParticipantAnswer.objects.create(
            participant_session=ps,
            question=self.question,
            selected_answer=self.answer,
            is_correct=True,
            points_earned=5,
        )
        self.assertEqual(answer.participant_session, ps)
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.selected_answer, self.answer)
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.points_earned, 5)
        self.assertIn(str(ps), str(answer))

    def test_unique_together_session_user(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="PQR678"
        )
        user = User.objects.create_user(
            username="player1",
            email="player1@testsession.com",
            password="pass12345!",
        )
        ParticipantSession.objects.create(session=session, user=user)
        with self.assertRaises(Exception):
            ParticipantSession.objects.create(session=session, user=user)

    def test_participant_answer_nullable_fields(self):
        session = QuizSession.objects.create(
            quiz=self.quiz, unique_code="STU901"
        )
        ps = ParticipantSession.objects.create(
            session=session, participant_name="Player"
        )
        answer = ParticipantAnswer.objects.create(
            participant_session=ps,
            question=self.question,
        )
        self.assertIsNone(answer.selected_answer)
        self.assertIsNone(answer.text_answer)
        self.assertFalse(answer.is_correct)
        self.assertEqual(answer.points_earned, 0)
