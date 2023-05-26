from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationForm
from users.models import CustomUser, Subscriptions


@register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    list_filter = (
        "first_name",
        "email",
    )
    ordering = ("username",)
    empty_value_display = "-пусто-"
    save_on_top = True


@register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
    search_fields = (
        "user",
        "author",
    )
    list_filter = (
        "user",
        "author",
    )
    empty_value_display = "-пусто-"
