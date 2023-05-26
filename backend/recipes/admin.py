from django.contrib import admin
from django.contrib.admin import register

from recipes.models import (AmountIngredient, Carts, Favorites, Ingredient,
                            Recipe, Tag)


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    search_fields = ("name", "color", "slug")
    list_filter = (
        "name",
        "color",
        "slug",
    )
    ordering = ("name",)
    empty_value_display = "-пусто-"


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name", "measurement_unit")
    list_filter = ("name",)
    ordering = ("id",)
    empty_value_display = "-пусто-"


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author", "count_favorites")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    ordering = ("name",)
    empty_value_display = "-пусто-"

    def count_favorites(self, obj):
        return obj.in_favorites.count()


@register(AmountIngredient)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredients", "amount")
    search_fields = (
        "recipe",
        "ingredients",
    )
    list_filter = (
        "recipe",
        "ingredients",
    )
    empty_value_display = "-пусто-"


@register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = (
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "recipe",
    )
    empty_value_display = "-пусто-"


@register(Carts)
class CartsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = (
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "recipe",
    )
    empty_value_display = "-пусто-"
