import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import AnswerVariant, Question, Quiz

User = get_user_model()


class IndexViewTests(TestCase):

    def test_index_accessible_by_anyone(self):
        resp = self.client.get(reverse("quizzes:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "index.html")

    def test_index_accessible_by_authenticated(self):
        user = User.objects.create_user(username="u", email="u@e.com",
                                        password="pass12345!", role="participant")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("quizzes:index")).status_code, 200)


class QuizCRUDPermissionMixin:
    _user_counter = 0

    def _unique_email(self, prefix="user"):
        QuizCRUDPermissionMixin._user_counter += 1
        return f"{prefix}{QuizCRUDPermissionMixin._user_counter}@example.com"

    def _create_organizer(self, username="org"):
        return User.objects.create_user(username=username,
                                        email=self._unique_email("org"),
                                        password="pass12345!", role="organizer")

    def _create_participant(self, username="part"):
        return User.objects.create_user(username=username,
                                        email=self._unique_email("part"),
                                        password="pass12345!", role="participant")

    def _create_quiz(self, creator, title="Test Quiz"):
        return Quiz.objects.create(title=title, description="Description",
                                   creator=creator, status="draft")


class MyQuizzesTests(QuizCRUDPermissionMixin, TestCase):

    def test_my_quizzes_anonymous_redirects(self):
        login, target = reverse("accounts:login"), reverse("quizzes:my_quizzes")
        self.assertRedirects(self.client.get(target), f"{login}?next={target}",
                             fetch_redirect_response=False)

    def test_my_quizzes_participant_redirects(self):
        self.client.force_login(self._create_participant())
        self.assertRedirects(self.client.get(reverse("quizzes:my_quizzes")),
                             reverse("quizzes:index"), fetch_redirect_response=False)

    def test_my_quizzes_organizer_shows_own_quizzes(self):
        user = self._create_organizer()
        self.client.force_login(user)
        quiz = self._create_quiz(creator=user)
        resp = self.client.get(reverse("quizzes:my_quizzes"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/my_quizzes.html")
        self.assertContains(resp, quiz.title)
        self.assertEqual(list(resp.context["quizzes"]), [quiz])

    def test_my_quizzes_organizer_does_not_see_others_quizzes(self):
        user = self._create_organizer()
        self._create_quiz(creator=self._create_organizer("org2"), title="Other Quiz")
        self.client.force_login(user)
        resp = self.client.get(reverse("quizzes:my_quizzes"))
        self.assertNotContains(resp, "Other Quiz")
        self.assertEqual(len(resp.context["quizzes"]), 0)


class QuizCreateTests(QuizCRUDPermissionMixin, TestCase):

    def test_create_get_anonymous_redirects(self):
        login, target = reverse("accounts:login"), reverse("quizzes:quiz_create")
        self.assertRedirects(self.client.get(target), f"{login}?next={target}",
                             fetch_redirect_response=False)

    def test_create_get_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.get(reverse("quizzes:quiz_create")).status_code, 403)

    def test_create_get_organizer_success(self):
        self.client.force_login(self._create_organizer())
        resp = self.client.get(reverse("quizzes:quiz_create"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/quiz_form.html")

    def test_create_post_anonymous_redirects(self):
        login, target = reverse("accounts:login"), reverse("quizzes:quiz_create")
        self.assertRedirects(self.client.post(target, {"title": "Test", "description": "Desc"}),
                             f"{login}?next={target}", fetch_redirect_response=False)

    def test_create_post_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.post(reverse("quizzes:quiz_create"),
                                          {"title": "Test", "description": "Desc"}).status_code, 403)

    def test_create_post_organizer_success(self):
        user = self._create_organizer()
        self.client.force_login(user)
        resp = self.client.post(reverse("quizzes:quiz_create"),
                                {"title": "New Quiz", "description": "Description text"})
        self.assertRedirects(resp, reverse("quizzes:my_quizzes"), fetch_redirect_response=False)
        self.assertTrue(Quiz.objects.filter(title="New Quiz", creator=user).exists())

    def test_create_post_invalid_data(self):
        user = self._create_organizer()
        self.client.force_login(user)
        resp = self.client.post(reverse("quizzes:quiz_create"), {"title": "", "description": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Quiz.objects.filter(creator=user).exists())


class QuizEditTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.edit_url = reverse("quizzes:quiz_edit", args=[self.quiz.id])

    def test_edit_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.get(self.edit_url), f"{login}?next={self.edit_url}",
                             fetch_redirect_response=False)

    def test_edit_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.get(self.edit_url).status_code, 403)

    def test_edit_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.get(self.edit_url).status_code, 404)

    def test_edit_owner_success(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/quiz_form.html")

    def test_edit_post_owner_updates(self):
        self.client.force_login(self.owner)
        resp = self.client.post(self.edit_url, {"title": "Updated Title", "description": "Updated"})
        self.assertRedirects(resp, reverse("quizzes:my_quizzes"), fetch_redirect_response=False)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "Updated Title")
        self.assertEqual(self.quiz.description, "Updated")


class QuizDeleteTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.delete_url = reverse("quizzes:quiz_delete", args=[self.quiz.id])

    def test_delete_get_owner_shows_confirm(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.delete_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/quiz_confirm_delete.html")

    def test_delete_post_owner_success(self):
        self.client.force_login(self.owner)
        resp = self.client.post(self.delete_url)
        self.assertRedirects(resp, reverse("quizzes:my_quizzes"), fetch_redirect_response=False)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())

    def test_delete_post_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.post(self.delete_url), f"{login}?next={self.delete_url}",
                             fetch_redirect_response=False)

    def test_delete_post_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)


class QuizPublishTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.publish_url = reverse("quizzes:quiz_publish", args=[self.quiz.id])

    def _add_question_with_answers(self, quiz):
        q = Question.objects.create(quiz=quiz, text="Test Q?", order=1)
        AnswerVariant.objects.create(question=q, text="A", is_correct=True, order=1)
        AnswerVariant.objects.create(question=q, text="B", is_correct=False, order=2)
        return q

    def test_publish_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.post(self.publish_url), f"{login}?next={self.publish_url}",
                             fetch_redirect_response=False)

    def test_publish_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.post(self.publish_url).status_code, 403)

    def test_publish_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.post(self.publish_url).status_code, 404)

    def test_publish_without_questions_redirects_to_edit(self):
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.post(self.publish_url),
                             reverse("quizzes:quiz_edit", args=[self.quiz.id]),
                             fetch_redirect_response=False)

    def test_publish_with_questions_success(self):
        self._add_question_with_answers(self.quiz)
        self.client.force_login(self.owner)
        resp = self.client.post(self.publish_url)
        self.assertRedirects(resp, reverse("quizzes:my_quizzes"), fetch_redirect_response=False)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.status, "published")

    def test_publish_get_redirects(self):
        self.client.force_login(self.owner)
        self.assertRedirects(self.client.get(self.publish_url), reverse("quizzes:my_quizzes"),
                             fetch_redirect_response=False)


class QuestionCreateTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.create_url = reverse("quizzes:question_create", args=[self.quiz.id])

    def test_create_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.get(self.create_url), f"{login}?next={self.create_url}",
                             fetch_redirect_response=False)

    def test_create_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.get(self.create_url).status_code, 403)

    def test_create_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.get(self.create_url).status_code, 404)

    def test_create_get_owner_success(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.create_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/question_form.html")

    def test_create_post_owner_success(self):
        self.client.force_login(self.owner)
        data = {"text": "Test Question?", "question_type": "single", "points": 1,
                "answer_variants-TOTAL_FORMS": "2", "answer_variants-INITIAL_FORMS": "0",
                "answer_variants-MIN_NUM_FORMS": "0", "answer_variants-MAX_NUM_FORMS": "1000",
                "answer_variants-0-text": "Correct Answer", "answer_variants-0-is_correct": "on",
                "answer_variants-0-order": "0", "answer_variants-1-text": "Wrong Answer",
                "answer_variants-1-is_correct": "", "answer_variants-1-order": "1"}
        resp = self.client.post(self.create_url, data)
        self.assertRedirects(resp, reverse("quizzes:quiz_edit", args=[self.quiz.id]),
                             fetch_redirect_response=False)
        self.assertEqual(self.quiz.questions.count(), 1)
        self.assertEqual(self.quiz.questions.first().text, "Test Question?")
        self.assertEqual(self.quiz.questions.first().answer_variants.count(), 2)

    def test_create_post_question_limit(self):
        self.client.force_login(self.owner)
        for i in range(100):
            Question.objects.create(quiz=self.quiz, text=f"Q{i}", order=i)
        resp = self.client.post(self.create_url, {"text": "Overflow Q", "question_type": "single", "points": 1})
        self.assertRedirects(resp, reverse("quizzes:quiz_edit", args=[self.quiz.id]),
                             fetch_redirect_response=False)
        self.assertEqual(self.quiz.questions.count(), 100)

    def test_create_post_invalid_data(self):
        self.client.force_login(self.owner)
        resp = self.client.post(self.create_url, {"text": "", "question_type": "single", "points": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.quiz.questions.count(), 0)


class QuestionEditTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.question = Question.objects.create(quiz=self.quiz, text="Original Q", order=1)
        self.edit_url = reverse("quizzes:question_edit", args=[self.quiz.id, self.question.id])

    def test_qedit_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.get(self.edit_url), f"{login}?next={self.edit_url}",
                             fetch_redirect_response=False)

    def test_qedit_participant_forbidden(self):
        self.client.force_login(self._create_participant())
        self.assertEqual(self.client.get(self.edit_url).status_code, 403)

    def test_qedit_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.get(self.edit_url).status_code, 404)

    def test_qedit_get_owner_success(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/question_form.html")
        self.assertFalse(resp.context["is_create"])

    def test_qedit_post_owner_updates(self):
        av1 = AnswerVariant.objects.create(question=self.question, text="A", is_correct=True, order=1)
        av2 = AnswerVariant.objects.create(question=self.question, text="B", is_correct=False, order=2)
        self.client.force_login(self.owner)
        data = {"text": "Updated Question", "question_type": "single", "points": 5,
                "answer_variants-TOTAL_FORMS": "2", "answer_variants-INITIAL_FORMS": "2",
                "answer_variants-MIN_NUM_FORMS": "0", "answer_variants-MAX_NUM_FORMS": "1000",
                "answer_variants-0-id": str(av1.id), "answer_variants-0-question": str(self.question.id),
                "answer_variants-0-text": "A", "answer_variants-0-is_correct": "on", "answer_variants-0-order": "0",
                "answer_variants-1-id": str(av2.id), "answer_variants-1-question": str(self.question.id),
                "answer_variants-1-text": "B", "answer_variants-1-is_correct": "", "answer_variants-1-order": "1"}
        resp = self.client.post(self.edit_url, data)
        self.assertRedirects(resp, reverse("quizzes:quiz_edit", args=[self.quiz.id]),
                             fetch_redirect_response=False)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Updated Question")
        self.assertEqual(self.question.points, 5)


class QuestionDeleteTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.question = Question.objects.create(quiz=self.quiz, text="To Delete", order=1)
        self.delete_url = reverse("quizzes:question_delete", args=[self.quiz.id, self.question.id])

    def test_qdelete_get_owner_shows_confirm(self):
        self.client.force_login(self.owner)
        resp = self.client.get(self.delete_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "quizzes/question_confirm_delete.html")

    def test_qdelete_post_owner_success(self):
        self.client.force_login(self.owner)
        resp = self.client.post(self.delete_url)
        self.assertRedirects(resp, reverse("quizzes:quiz_edit", args=[self.quiz.id]),
                             fetch_redirect_response=False)
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())

    def test_qdelete_post_anonymous_redirects(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.post(self.delete_url), f"{login}?next={self.delete_url}",
                             fetch_redirect_response=False)

    def test_qdelete_post_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)

    def test_qdelete_last_question_downgrades_published_quiz(self):
        self.quiz.status = "published"
        self.quiz.save()
        self.client.force_login(self.owner)
        self.client.post(self.delete_url)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.status, "draft")


class QuestionReorderTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.q1 = Question.objects.create(quiz=self.quiz, text="Q1", order=1)
        self.q2 = Question.objects.create(quiz=self.quiz, text="Q2", order=2)
        self.reorder_url = reverse("quizzes:question_reorder", args=[self.quiz.id])

    def test_qreorder_anonymous_redirects(self):
        login = reverse("accounts:login")
        payload = json.dumps({"order": [{"id": self.q1.id, "order": 2}]})
        self.assertRedirects(self.client.post(self.reorder_url, payload,
                             content_type="application/json"),
                             f"{login}?next={self.reorder_url}", fetch_redirect_response=False)

    def test_qreorder_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        payload = json.dumps({"order": [{"id": self.q1.id, "order": 2}]})
        self.assertEqual(self.client.post(self.reorder_url, payload,
                                          content_type="application/json").status_code, 404)

    def test_qreorder_owner_success(self):
        self.client.force_login(self.owner)
        payload = json.dumps({"order": [{"id": self.q1.id, "order": 2},
                                       {"id": self.q2.id, "order": 1}]})
        resp = self.client.post(self.reorder_url, payload, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)["status"], "ok")
        self.q1.refresh_from_db()
        self.q2.refresh_from_db()
        self.assertEqual(self.q1.order, 2)
        self.assertEqual(self.q2.order, 1)

    def test_qreorder_get_not_allowed(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.reorder_url).status_code, 405)


class AnswerVariantReorderTests(QuizCRUDPermissionMixin, TestCase):

    def setUp(self):
        self.owner = self._create_organizer("owner")
        self.quiz = self._create_quiz(creator=self.owner)
        self.question = Question.objects.create(quiz=self.quiz, text="Q?", order=1)
        self.a1 = AnswerVariant.objects.create(question=self.question, text="A", order=1)
        self.a2 = AnswerVariant.objects.create(question=self.question, text="B", order=2)
        self.reorder_url = reverse("quizzes:answer_variant_reorder", args=[self.question.id])

    def test_avreorder_anonymous_redirects(self):
        login = reverse("accounts:login")
        payload = json.dumps({"order": [{"id": self.a1.id, "order": 2}]})
        self.assertRedirects(self.client.post(self.reorder_url, payload,
                             content_type="application/json"),
                             f"{login}?next={self.reorder_url}", fetch_redirect_response=False)

    def test_avreorder_other_organizer_not_found(self):
        self.client.force_login(self._create_organizer("other"))
        payload = json.dumps({"order": [{"id": self.a1.id, "order": 2}]})
        self.assertEqual(self.client.post(self.reorder_url, payload,
                                          content_type="application/json").status_code, 404)

    def test_avreorder_owner_success(self):
        self.client.force_login(self.owner)
        payload = json.dumps({"order": [{"id": self.a1.id, "order": 2},
                                       {"id": self.a2.id, "order": 1}]})
        resp = self.client.post(self.reorder_url, payload, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)["status"], "ok")
        self.a1.refresh_from_db()
        self.a2.refresh_from_db()
        self.assertEqual(self.a1.order, 2)
        self.assertEqual(self.a2.order, 1)

    def test_avreorder_get_not_allowed(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.reorder_url).status_code, 405)


class PermissionTests(QuizCRUDPermissionMixin, TestCase):

    def test_participant_gets_403_on_organizer_views(self):
        self.client.force_login(self._create_participant())
        for url in [reverse("quizzes:quiz_create")]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_anonymous_gets_redirected_to_login(self):
        login_url = reverse("accounts:login")
        for url in [reverse("quizzes:my_quizzes"), reverse("quizzes:quiz_create")]:
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), f"{login_url}?next={url}",
                                     fetch_redirect_response=False)
