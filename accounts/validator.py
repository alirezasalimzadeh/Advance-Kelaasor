from django.core.exceptions import ValidationError

def validate_phone_number(value):
    if not value.isdigit():
        raise ValidationError("Phone number must contain only digits.")
    if len(value) != 11:
        raise ValidationError("Phone number must be exactly 11 digits.")
    if not value.startswith("09"):
        raise ValidationError("Phone number must start with 09.")
