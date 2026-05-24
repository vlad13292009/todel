import test_setup

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_register_organizer_get(self):
        response = self.client.get(reverse("accounts:register_organizer"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register_form.html")
        self.assertEqual(response.context["role"], "organizer")

    def test_register_participant_get(self):
        response = self.client.get(reverse("accounts:register_participant"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register_form.html")
        self.assertEqual(response.context["role"], "participant")

    def test_register_organizer_post_success(self):
        data = {
            "username": "org1",
            "email": "org1@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        response = self.client.post(reverse("accounts:register_organizer"), data)
        self.assertRedirects(
            response, reverse("quizzes:my_quizzes"), fetch_redirect_response=False
        )
        user = User.objects.get(username="org1")
        self.assertEqual(user.role, "organizer")
        self.assertTrue(user.is_authenticated)

    def test_register_participant_post_success(self):
        data = {
            "username": "part1",
            "email": "part1@example.com",
            "password1": "testpass123!",
            "password2": "testpass123!",
        }
        response = self.client.post(reverse("accounts:register_participant"), data)
        self.assertRedirects(
            response, reverse("quizzes:index"), fetch_redirect_response=False
        )
        user = User.objects.get(username="part1")
        self.assertEqual(user.role, "participant")

    def test_register_organizer_post_invalid(self):
        data = {
            "username": "",
            "email": "invalid",
            "password1": "short",
            "password2": "mismatch",
        }
        response = self.client.post(reverse("accounts:register_organizer"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="invalid").exists())

    def test_authenticated_user_redirected_from_register_organizer(self):
        user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="pass12345!",
            role="participant",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:register_organizer"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_redirected_from_register_participant(self):
        user = User.objects.create_user(
            username="existing2",
            email="existing2@example.com",
            password="pass12345!",
            role="organizer",
        )
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:register_participant"))
        self.assertEqual(response.status_code, 302)


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123!",
            role="participant",
        )

    def test_login_get(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_post_success_participant(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123!"},
        )
        self.assertRedirects(
            response, reverse("quizzes:index"), fetch_redirect_response=False
        )

    def test_login_post_success_organizer(self):
        organizer = User.objects.create_user(
            username="org",
            email="org@example.com",
            password="orgpass123!",
            role="organizer",
        )
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "org", "password": "orgpass123!"},
        )
        self.assertRedirects(
            response, reverse("quizzes:my_quizzes"), fetch_redirect_response=False
        )

    def test_login_post_invalid(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный логин или пароль")

    def test_authenticated_user_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:login"))
        self.assertRedirects(
            response, reverse("quizzes:index"), fetch_redirect_response=False
        )


class LogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123!",
        )

    def test_logout_post_success(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response, reverse("accounts:login"), fetch_redirect_response=False
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_get_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_logout_anonymous_redirects(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:logout')}",
            fetch_redirect_response=False,
        )


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123!",
        )

    def test_profile_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertEqual(response.context["user"], self.user)

    def test_profile_anonymous_redirects(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:profile')}",
            fetch_redirect_response=False,
        )
