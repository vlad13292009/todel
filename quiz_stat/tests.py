from django.apps import apps
from django.test import TestCase


class QuizStatAppTests(TestCase):
    def test_app_config(self):
        app_config = apps.get_app_config("quiz_stat")
        self.assertEqual(app_config.name, "quiz_stat")
