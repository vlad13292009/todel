from django.db import models
from quizzes.models import Quiz, Question, AnswerVariant
from accounts.models import CustomUser
from django.db.models import Count, Q, Sum, Min, Max

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
    total_score = models.IntegerField(default=0, verbose_name="Всего баллов")
    correct_answers_count = models.IntegerField(default=0, verbose_name="Правильных ответов")
    incorrect_answers_count = models.IntegerField(default=0, verbose_name="Неправильных ответов")
    skipped_answers_count = models.PositiveIntegerField(default=0, verbose_name="Пропущено вопросов")
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Всего вопросов")
    time_spent_seconds = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Время прохождения (сек)"
    )
    score_percent = models.FloatField(
        null=True, blank=True, verbose_name="Процент правильных"
    )
    place_in_rating = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Место в рейтинге"
    )
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Завершил")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Подключился")

    class Meta:
        verbose_name = "Участие в сессии"
        verbose_name_plural = "Участия в сессиях"
        unique_together = ['session', 'user']
        ordering = ['-total_score', 'time_spent_seconds']

    def __str__(self):
        name = self.user.username if self.user else self.participant_name
        return f"{name} in {self.session.unique_code}"

    def calculate_and_save_stats(self):
        from django.db.models import Count, Q, Sum, Min, Max

        answers_agg = self.answers.aggregate(
            correct=Count('id', filter=Q(is_correct=True)),
            incorrect=Count('id', filter=Q(is_correct=False)),
            skipped=Count('id', filter=Q(selected_answer__isnull=True, text_answer__exact='')),
            total=Count('id'),
            points=Sum('points_earned'),
            first_answered_at=Min('answered_at'),
            last_answered_at=Max('answered_at')
        )

        self.total_questions = answers_agg['total'] or 0
        self.correct_answers_count = answers_agg['correct'] or 0
        self.incorrect_answers_count = answers_agg['incorrect'] or 0
        self.skipped_answers_count = answers_agg['skipped'] or 0
        self.total_score = answers_agg['points'] or 0

        if answers_agg['first_answered_at'] and answers_agg['last_answered_at']:
            self.time_spent_seconds = int(
                (answers_agg['last_answered_at'] - answers_agg['first_answered_at']).total_seconds()
            )

        if self.total_questions > 0:
            self.score_percent = round(
                (self.correct_answers_count / self.total_questions) * 100, 2
            )

        self.save(update_fields=[
            'total_questions', 'correct_answers_count', 'incorrect_answers_count',
            'skipped_answers_count', 'total_score', 'time_spent_seconds', 'score_percent'
        ])

    def finish_session(self):
        from django.utils import timezone
        self.finished_at = timezone.now()
        self.calculate_and_save_stats()
        self.save(update_fields=['finished_at'])

    def get_detailed_results(self):
        results = []
        for answer in self.answers.select_related('question', 'selected_answer').order_by('answered_at'):
            results.append({
                'question_text': answer.question.text,
                'question_type': answer.question.question_type,
                'selected': answer.selected_answer.text if answer.selected_answer else answer.text_answer,
                'correct_answers': [a.text for a in answer.question.answer_variants.filter(is_correct=True)],
                'is_correct': answer.is_correct,
                'points': answer.points_earned,
                'answered_at': answer.answered_at,
            })
        return results


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
