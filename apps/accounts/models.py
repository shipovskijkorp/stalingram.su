from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Theme(models.TextChoices):
        LIGHT = "light", "Светлая"
        DARK = "dark", "Тёмная"

    email = models.EmailField("электронная почта", unique=True)
    bio = models.CharField("о себе", max_length=160, blank=True, default="")
    avatar = models.ImageField(
        "фотография профиля",
        upload_to="avatars/%Y/%m/",
        blank=True,
        default="",
    )
    theme = models.CharField(
        "тема оформления",
        max_length=10,
        choices=Theme.choices,
        default=Theme.LIGHT,
    )
    enter_to_send = models.BooleanField("отправка по Enter", default=True)

    @property
    def display_name(self):
        return self.get_full_name().strip() or self.username

    @property
    def initials(self):
        parts = self.get_full_name().split()
        if parts:
            return "".join(part[0] for part in parts[:2]).upper()
        return self.username[:2].upper() or "?"

    def __str__(self):
        return self.username
