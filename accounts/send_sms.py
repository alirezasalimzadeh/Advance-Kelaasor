from kavenegar import KavenegarAPI
from django.conf import settings

def send_sms(phone: str, text: str) -> bool:
    """
    Send an SMS using Kavenegar API.
    Prints message in development mode, sends real SMS in production.
    Returns True if successful, False otherwise.
    """
    if settings.DEBUG:
        print(text)
        return True

    try:
        api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
        api.sms_send({
            'sender': settings.KAVENEGAR_SENDER,
            'receptor': phone,
            'message': text,
        })
        return True
    except Exception:
        return False
