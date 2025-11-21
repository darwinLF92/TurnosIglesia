import os
from twilio.rest import Client

def enviar_whatsapp_twilio(para_e164: str, cuerpo: str):
    sid = os.getenv("TWILIO_CUENTA_SID")
    token = os.getenv("TWILIO_TOKEN_AUT")
    desde = os.getenv("TWILIO_WHATSAPP_DESDE")  # ej: "whatsapp:+14155238886"
    cli = Client(sid, token)
    return cli.messages.create(body=cuerpo, from_=desde, to=f"whatsapp:{para_e164}")
