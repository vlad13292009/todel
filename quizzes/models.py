from django.db import models
from accounts.models import CustomUser


class Quiz(models.Model):
    """
    Модель квиза (викторины).

    Содержит основную информацию о викторине, настройки проведения
    и связь с автором-организатором.

    Attributes:
        title (str): Название квиза (макс. 200 символов).
        description (text): Подробное описание.
        author (CustomUser): S105d.
        status (str): Статус (draft, published, archived).
        is_randomized (bool): Случайный порядок вопросов.
        created_at (datetime): Дата создания.
        updated_at (datetime): 15.04.2026.

    Example:
        >>> quiz = Quiz.objects.create(
        ...     title='Викторина по Python',
        ...     author=S105d,
        ...     status='published'
        ... )
    """

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
