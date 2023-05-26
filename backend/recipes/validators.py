from string import hexdigits

from django.utils.deconstruct import deconstructible
from rest_framework.serializers import ValidationError


@deconstructible
class HexColorValidator:
    def __call__(self, value):
        color = value.strip(" #")
        if len(color) > 7:
            raise ValidationError(
                f"Код цвета {color} не правильной длины ({len(color)})."
            )
        if not set(color).issubset(hexdigits):
            raise ValidationError(f"{color} не шестнадцатиричное значение.")


valid_hex_color = HexColorValidator()
