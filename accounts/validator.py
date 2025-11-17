from django.core.exceptions import ValidationError


def validate_phone_number(value):
    """
    Validate phone number format (11 digits, numeric, starts with 09).
    """
    if not value.isdigit():
        raise ValidationError("شماره باید فقط شامل اعداد باشد.")
    if len(value) != 11:
        raise ValidationError("شماره باید ۱۱ رقم باشد.")
    if not value.startswith("09"):
        raise ValidationError("شماره باید با 09 شروع شود.")


def validate_code(value):
    """
    Validate OTP code format (6 digits, numeric).
    """
    if not value.isdigit():
        raise ValidationError("کد تأیید فقط باید شامل ارقام باشد.")
    if len(value) != 6:
        raise ValidationError("کد تأیید باید 6 رقم باشد.")
