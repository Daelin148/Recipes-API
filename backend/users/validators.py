import re

from django.core.exceptions import ValidationError

from .constants import FORBIDDEN_NAME, REGEX_USERNAME


def validate_username(value):
    if value.lower() == FORBIDDEN_NAME:
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )
    if not bool(re.match(REGEX_USERNAME, value)):
        raise ValidationError(
            'Некорректные символы в username'
        )
    return value
