import re

from django.utils.deconstruct import deconstructible
from rest_framework.serializers import ValidationError


@deconstructible
class UsernameValidator:
    user_regex = re.compile(r"^[\w.@+-]+\Z")

    def __call__(self, value):
        if value.lower() == "me":
            raise ValidationError(
                "Использовать 'me' в качестве username запрещено.",
                code="не верное значение",
            )

        if not self.user_regex.match(value):
            raise ValidationError(
                "Разрешены только буквы/цифры/_/- ", code="не верное значение"
            )


valid_username = UsernameValidator()
