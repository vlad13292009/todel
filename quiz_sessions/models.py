from django.db import models
from quizzes.models import Quiz, Question, AnswerVariant
from accounts.models import CustomUser


class QuizSession(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Квиз"
    )
    unique_code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Уникальный код для входа"
    )
    password = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Пароль сессии"
    )
    SESSION_STATUS_CHOICES = [
        ('waiting', 'Ожидание'),
        ('active', 'Активна'),
        ('finished', 'Завершена'),
    ]
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default='waiting',
        verbose_name="Статус"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Начало"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершение"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создана"
    )

    class Meta:
        verbose_name = "Сессия квиза"
        verbose_name_plural = "Сессии квизов"

    def __str__(self):
        return f"{self.quiz.title} - {self.unique_code}"


class ParticipantSession(models.Model):
    session = models.ForeignKey(
        QuizSession,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name="Сессия"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='participant_sessions',
        verbose_name="Пользователь"
    )
    participant_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя участника"
    )
    total_score = models.IntegerField(
        default=0,
        verbose_name="Всего баллов"
    )
    correct_answers_count = models.IntegerField(
        default=0,
        verbose_name="Правильных ответов"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершил"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Подключился"
    )

    class Meta:
        verbose_name = "Участие в сессии"
        verbose_name_plural = "Участия в сессиях"
        unique_together = ['session', 'user']

    def __str__(self):
        if self.user:
            return f"{self.user.username} in {self.session.unique_code}"
        return f"{self.participant_name} in {self.session.unique_code}"


class ParticipantAnswer(models.Model):
    participant_session = models.ForeignKey(
        ParticipantSession,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Участник сессии"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Вопрос"
    )
    selected_answer = models.ForeignKey(
        AnswerVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Выбранный ответ"
    )
    text_answer = models.TextField(
        null=True,
        blank=True,
        verbose_name="Текстовый ответ"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ"
    )
    points_earned = models.IntegerField(
        default=0,
        verbose_name="Получено баллов"
    )
    answered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время ответа"
    )

    class Meta:
        verbose_name = "Ответ участника"
        verbose_name_plural = "Ответы участников"
        ordering = ['answered_at']

    def __str__(self):
        return f"Answer by {self.participant_session} on {self.question}"
