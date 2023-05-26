from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, Model, Q, UniqueConstraint)

from .validators import valid_username


class CustomUser(AbstractUser):
    email = EmailField(
        verbose_name="Адрес электронной почты",
        max_length=254,
        unique=True,
        error_messages={
            "unique": "Пользователь с таким e-mail уже существует.",
        },
        help_text="Обязательное для заполнения поле. Максимум 254 символа.",
        validators=(MaxLengthValidator(254),),
    )
    username = CharField(
        verbose_name="Уникальный юзернейм",
        max_length=150,
        unique=True,
        error_messages={
            "unique": "Пользователь с таким username уже существует.",
        },
        help_text="Обязательное для заполнения поле. Максимум 150 символов.",
        validators=(
            MaxLengthValidator(150),
            valid_username,
        ),
    )
    first_name = CharField(
        verbose_name="Имя",
        max_length=150,
        help_text="Обязательное для заполнения поле. Максимум 150 символов.",
        validators=(MaxLengthValidator(150),),
    )
    last_name = CharField(
        verbose_name="Фамилия",
        max_length=150,
        help_text="Обязательное для заполнения поле. Максимум 150 символов.",
        validators=(MaxLengthValidator(150),),
    )
    password = CharField(
        verbose_name="Пароль",
        max_length=150,
        help_text="Обязательное для заполнения поле. Максимум 150 символов.",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "password",
        "first_name",
        "last_name",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
        constraints = (
            UniqueConstraint(
                fields=["email", "username"],
                name="unique_email_username",
            ),
        )

    def __str__(self) -> str:
        return f"{self.username}: {self.email}"


class Subscriptions(Model):
    author = ForeignKey(
        to=CustomUser,
        verbose_name="Автор рецепта",
        related_name="subscribers",
        on_delete=CASCADE,
    )
    user = ForeignKey(
        to=CustomUser,
        verbose_name="Подписчик",
        related_name="subscriptions",
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            UniqueConstraint(
                fields=("author", "user"),
                name="unique_subscription",
            ),
            CheckConstraint(
                check=~Q(author=F("user")),
                name="self_sibscription",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user.username} подписан на {self.author.username}"
