from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db.models import (CASCADE, SET_NULL, CharField, DateTimeField,
                              ForeignKey, ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, TextField,
                              UniqueConstraint)

from .validators import valid_hex_color

User = get_user_model()


class Tag(Model):
    name = CharField(
        verbose_name="Название тега",
        max_length=200,
        unique=True,
        error_messages={
            "unique": "Тег с таким названием уже существует.",
        },
        help_text="Обязательное для заполнения поле. Максимум 200 символов.",
        validators=(
            MaxLengthValidator(200),
            valid_hex_color,
        ),
    )
    color = CharField(
        verbose_name="Цвет в HEX",
        max_length=7,
        unique=True,
        error_messages={
            "unique": "Тег с таким цветом уже существует.",
        },
        help_text="Обязательное для заполнения поле. Максимум 7 символов.",
        validators=(
            MaxLengthValidator(7),
            valid_hex_color,
        ),
        default="#008080",
    )
    slug = CharField(
        verbose_name="Уникальный слаг",
        max_length=200,
        unique=True,
        error_messages={
            "unique": "Тег с таким слагом уже существует.",
        },
        help_text="Обязательное для заполнения поле. Максимум 200 символов.",
        validators=(MaxLengthValidator(200),),
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} (цвет: {self.color})"


class Ingredient(Model):
    name = CharField(
        verbose_name="Ингредиент",
        max_length=200,
        help_text="Обязательное для заполнения поле. Максимум 200 символов.",
        validators=(MaxLengthValidator(200),),
    )
    measurement_unit = CharField(
        verbose_name="Единица измерения",
        max_length=200,
        help_text="Обязательное для заполнения поле. Максимум 200 символов.",
        validators=(MaxLengthValidator(200),),
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = (
            UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_measurement",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name} {self.measurement_unit}"


class Recipe(Model):
    name = CharField(
        verbose_name="Название рецепта",
        max_length=200,
        help_text="Обязательное для заполнения поле. Максимум 200 символов.",
        validators=(MaxLengthValidator(200),),
    )
    author = ForeignKey(
        to=User,
        verbose_name="Автор рецепта",
        related_name="recipes",
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        to=Tag,
        verbose_name="Теги",
        related_name="recipes",
    )
    ingredients = ManyToManyField(
        to=Ingredient,
        through="recipes.AmountIngredient",
        verbose_name="Ингредиенты рецепта",
        related_name="recipes",
    )
    pub_date = DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        verbose_name="Изображение рецепта",
        upload_to="recipe_images/",
    )
    text = TextField(
        verbose_name="Описание рецепта",
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name="Время приготовления в минутах",
        default=0,
        validators=(
            MinValueValidator(
                1,
                "Минимальное время приготовления 1 минута",
            ),
        ),
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)
        constraints = (
            UniqueConstraint(
                fields=("name", "author"),
                name="unique_recipe_author",
            ),
        )

    def __str__(self) -> str:
        return f"{self.name}. Автор: {self.author.username}"


class AmountIngredient(Model):
    recipe = ForeignKey(
        to=Recipe,
        verbose_name="Рецепт",
        related_name="ingredient",
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        to=Ingredient,
        verbose_name="Ингредиент",
        related_name="recipe",
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name="Количество",
        default=0,
        validators=(
            MinValueValidator(
                1,
                "Минимальное количество 1.",
            ),
        ),
    )

    class Meta:
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество Ингредиентов"
        ordering = ("recipe",)
        constraints = (
            UniqueConstraint(
                fields=("recipe", "ingredients"),
                name="unique_recipe_ingredients",
            ),
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredients}"


class Favorites(Model):
    recipe = ForeignKey(
        to=Recipe,
        verbose_name="Избранные рецепты",
        related_name="in_favorites",
        on_delete=CASCADE,
    )
    user = ForeignKey(
        to=User,
        verbose_name="Пользователь",
        related_name="favorites",
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="unique_favorite_recipe_user",
            ),
        )

    def __str__(self) -> str:
        return f"Рецепт {self.recipe} в избранном у{self.user}"


class Carts(Model):
    recipe = ForeignKey(
        to=Recipe,
        verbose_name="Рецепты в списке покупок",
        related_name="in_carts",
        on_delete=CASCADE,
    )
    user = ForeignKey(
        to=User,
        verbose_name="Автор списка покупок",
        related_name="carts",
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name="Дата добавления", auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = "Рецепт в списке покупок"
        verbose_name_plural = "Рецепты в списке покупок"
        constraints = (
            UniqueConstraint(
                fields=(
                    "recipe",
                    "user",
                ),
                name="unique_cart_recipe_user",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user} -> {self.recipe}"
