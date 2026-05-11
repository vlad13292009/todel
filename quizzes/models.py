from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from accounts.models import CustomUser


class Quiz(models.Model):
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(3, message="Название должно содержать минимум 3 символа")
        ],
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True, verbose_name="Описание", validators=[MaxLengthValidator(1000)]
    )
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Создатель",
    )
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликован"),
        ("archived", "Архивный"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Статус",
    )
    image = models.ImageField(
        upload_to="quiz_covers/", blank=True, null=True, verbose_name="Обложка"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.status == "published" and self.questions.count() == 0:
            raise ValidationError(
                "Опубликованный квиз должен содержать хотя бы один вопрос."
            )
        if self.pk and self.questions.count() > 100:
            raise ValidationError(
                {"title": "Квиз не может содержать более 100 вопросов."}
            )


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Квиз",
    )
    text = models.TextField(
        verbose_name="Текст вопроса",
        validators=[MaxLengthValidator(500)],
    )
    QUESTION_TYPE_CHOICES = [
        ("single", "Один правильный ответ"),
        ("multiple", "Несколько правильных ответов"),
        ("text", "Текстовый ответ"),
    ]
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default="single",
        verbose_name="Тип вопроса",
    )
    points = models.PositiveIntegerField(default=1, verbose_name="Баллы")
    timer = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Таймер (секунды)",
    )
    image = models.ImageField(
        upload_to="question_images/",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]

    def clean(self):
        super().clean()
        if not self.pk:
            return
        variants = self.answer_variants.all()
        if variants.count() < 2:
            raise ValidationError("Вопрос должен иметь минимум 2 варианта ответа.")
        if not variants.filter(is_correct=True).exists():
            raise ValidationError("Должен быть хотя бы один правильный ответ.")
        if (
            self.question_type == "single"
            and variants.filter(is_correct=True).count() > 1
        ):
            raise ValidationError(
                "Для вопроса с одним правильным ответом может быть только один "
                "верный вариант.",
            )


class AnswerVariant(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answer_variants",
        verbose_name="Вопрос",
    )
    text = models.CharField(max_length=255, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")
    image = models.ImageField(
        upload_to="answer_images/", blank=True, null=True, verbose_name="Изображение"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ["order"]

    def __str__(self):
        return f"{self.text[:30]}... {'✓' if self.is_correct else ''}"
