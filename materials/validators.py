import re

from rest_framework.serializers import ValidationError

# forbidden_reference = ["youtube.com"]

def validate_forbidden_reference(value):
    # if value not in forbidden_reference:
    if not re.search(r'youtube\.com', value, re.IGNORECASE):
        raise ValidationError("Запрещено использовать ссылки на все ресурсы, кроме 'youtube.com'.")