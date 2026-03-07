from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = [
        ('organizer', 'Организатор'),
        ('participant', 'Участник'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='participant',
        verbose_name="Роль"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
