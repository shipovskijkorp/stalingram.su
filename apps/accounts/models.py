from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("электронная почта", unique=True)
    bio = models.CharField("о себе", max_length=160, blank=True, default="")
    avatar = models.ImageField(
        "фотография профиля",
        upload_to="avatars/%Y/%m/",
        blank=True,
        default="",
    )

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
