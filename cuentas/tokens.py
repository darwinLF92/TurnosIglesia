# cuentas/tokens.py
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core import signing
from django.conf import settings

_signer = TimestampSigner(salt="email-confirm-v1")
RESET_SALT = "password-reset-v1"

def make_email_token(user_id: int) -> str:
    # devuelve "valor:firmado" (string seguro para URL, y corto)
    return _signer.sign(str(user_id))

def read_email_token(token: str, max_age=60*60*24) -> int:
    # 24h por defecto
    unsigned = _signer.unsign(token, max_age=max_age)  # lanza si expira o es inválido
    return int(unsigned)

def make_reset_password_token(user_id: int) -> str:
    """
    Genera un token firmado con el ID del usuario.
    """
    data = {"uid": user_id}
    return signing.dumps(data, salt=RESET_SALT)


def read_reset_password_token(token: str, max_age: int = 60 * 60 * 24) -> int:
    """
    Lee el token y devuelve el user_id.
    max_age = segundos de validez (aquí 24 horas).
    Puede lanzar SignatureExpired o BadSignature.
    """
    data = signing.loads(token, salt=RESET_SALT, max_age=max_age)
    return data["uid"]