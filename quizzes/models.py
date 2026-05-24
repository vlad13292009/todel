from django.db import models
from accounts.models import CustomUser


class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Создатель"
    )
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'Архивный'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус"
    )
    image = models.ImageField(
        upload_to='quiz_covers/',
        blank=True,
        null=True,
        verbose_name="Обложка"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Квиз"
    )
    text = models.TextField(verbose_name="Текст вопроса")

    QUESTION_TYPE_CHOICES = [
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('text', 'Текстовый ответ'),
    ]
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='single',
        verbose_name="Тип вопроса"
    )

    points = models.PositiveIntegerField(
        default=1,
        verbose_name="Баллы"
    )

    timer = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Таймер (секунды)",
        help_text="Оставьте пустым, если время не ограничено"
    )

    image = models.ImageField(
        upload_to='question_images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['order']

    def __str__(self):
        return self.text[:50]


class AnswerVariant(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answer_variants',
        verbose_name="Вопрос"
    )
    text = models.CharField(
        max_length=255,
        verbose_name="Текст ответа"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ"
    )
    image = models.ImageField(
        upload_to='answer_images/',
        blank=True,
        null=True,
        verbose_name="Изображение"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:30]}... {'✓' if self.is_correct else ''}"

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class QuestionTemplate(models.Model):
    ANSWER_TYPE_SINGLE_CHOICE = 'single'
    ANSWER_TYPE_MULTI_CHOICE = 'multi'
    ANSWER_TYPE_TEXT = 'text'
    ANSWER_TYPE_CHOICES = [
        (ANSWER_TYPE_SINGLE_CHOICE, 'Single Choice'),
        (ANSWER_TYPE_MULTI_CHOICE, 'Multi Choice'),
        (ANSWER_TYPE_TEXT, 'Text Input'),
    ]

    text = models.TextField()
    answer_type = models.CharField(max_length=10, choices=ANSWER_TYPE_CHOICES)
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='question_templates')
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text
