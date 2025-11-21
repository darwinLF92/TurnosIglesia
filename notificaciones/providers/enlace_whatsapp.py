import urllib.parse

def enlace_click_to_chat(telefono_e164: str, texto: str):
    q = urllib.parse.urlencode({"phone": telefono_e164.replace("+",""), "text": texto})
    return f"https://wa.me/?{q}"
