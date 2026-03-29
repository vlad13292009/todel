from django.db import models

from quizzes.models import Question


class QuestionStats(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name='Вопрос'
    )
    correct_answers_count = models.IntegerField(default=0, verbose_name='Правильных ответов')
    total_attempts = models.IntegerField(default=0, verbose_name='Всего попыток')
    total_time_spent = models.FloatField(default=0.0, verbose_name='Общее время (сек)')
    difficulty = models.IntegerField(default=1, verbose_name='Сложность (1-5)')

    @property
    def accuracy_rate(self):
        """Процент правильных ответов"""
        if self.total_attempts == 0:
            return 0.0
        return round((self.correct_answers_count / self.total_attempts) * 100, 2)

    @property
    def avg_response_time(self):
        """Среднее время ответа"""
        if self.total_attempts == 0:
            return 0.0
        return round(self.total_time_spent / self.total_attempts, 2)

    class Meta:
        verbose_name = 'Статистика вопроса'
        verbose_name_plural = 'Статистика вопросов'

    def __str__(self):
        return f"Статистика для: {self.question.text[:30]}"

