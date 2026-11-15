"""Interface text in each supported language, and a light message-language guess."""
import re

LANGS = {"English": "en", "Español": "es", "中文": "zh"}
LANG_NAMES = {"en": "English", "es": "Spanish", "zh": "Simplified Chinese"}

T = {
    "en": {
        "tagline": "Look twice before you tap.",
        "intro": "Got a text you're not sure about? Paste it here and SecondLook will tell you if it looks like a scam, and why.",
        "lang_label": "Explain in",
        "box_label": "The text message",
        "box_placeholder": "Paste the message here",
        "button": "Check this message",
        "examples": "Or try an example",
        "stamp": {"scam": "SCAM", "suspicious": "BE CAREFUL", "safe": "SAFE"},
        "signs": "Warning signs",
        "translation": "The message in English",
        "how_agent": "Checked by the Claude agent, which inspected the links and compared the message with known scam types.",
        "how_layer1": "Checked by our on-device model. No warning signs, so it wasn't sent anywhere else.",
        "safe_expl": "No warning signs found. This looks like a normal message.",
        "risky_expl": "Our model thinks this may be a scam. Don't tap any links. Contact the company through its official website or the number on your card.",
        "inconclusive": "We couldn't finish checking this message. Treat it with care: don't tap links, and contact the company through its official website.",
        "cap_note": "Today's checking limit has been reached, so only our on-device model was used.",
        "no_key_note": "The Claude agent isn't connected, so only our on-device model was used.",
        "empty": "Paste a text message first, then press “Check this message”.",
        "disclaimer": "SecondLook is a student prototype and is not financial advice. Only paste messages you're allowed to share.",
    },
    "es": {
        "tagline": "Mire dos veces antes de tocar.",
        "intro": "¿Recibió un mensaje que le da dudas? Péguelo aquí y SecondLook le dirá si parece una estafa y por qué.",
        "lang_label": "Explicar en",
        "box_label": "El mensaje de texto",
        "box_placeholder": "Pegue el mensaje aquí",
        "button": "Revisar este mensaje",
        "examples": "O pruebe un ejemplo",
        "stamp": {"scam": "ESTAFA", "suspicious": "CUIDADO", "safe": "SEGURO"},
        "signs": "Señales de alerta",
        "translation": "El mensaje en español",
        "how_agent": "Revisado por el agente Claude, que examinó los enlaces y comparó el mensaje con estafas conocidas.",
        "how_layer1": "Revisado por nuestro modelo local. No hubo señales de alerta, así que no se envió a ningún otro lugar.",
        "safe_expl": "No encontramos señales de alerta. Parece un mensaje normal.",
        "risky_expl": "Nuestro modelo cree que esto puede ser una estafa. No toque ningún enlace. Comuníquese con la empresa por su sitio web oficial o el número de su tarjeta.",
        "inconclusive": "No pudimos terminar de revisar este mensaje. Tenga cuidado: no toque enlaces y comuníquese con la empresa por su sitio web oficial.",
        "cap_note": "Se alcanzó el límite de revisiones de hoy, así que solo se usó nuestro modelo local.",
        "no_key_note": "El agente Claude no está conectado, así que solo se usó nuestro modelo local.",
        "empty": "Primero pegue un mensaje de texto y luego toque “Revisar este mensaje”.",
        "disclaimer": "SecondLook es un prototipo estudiantil y no es asesoría financiera. Pegue solo mensajes que tenga permiso de compartir.",
    },
    "zh": {
        "tagline": "点开之前，再看一眼。",
        "intro": "收到拿不准的短信？粘贴到这里，SecondLook 会告诉您它像不像诈骗，以及原因。",
        "lang_label": "解释语言",
        "box_label": "短信内容",
        "box_placeholder": "把短信粘贴到这里",
        "button": "检查这条短信",
        "examples": "或者试一个例子",
        "stamp": {"scam": "诈骗", "suspicious": "小心", "safe": "安全"},
        "signs": "可疑迹象",
        "translation": "短信的中文翻译",
        "how_agent": "由 Claude 智能助手检查：它查看了链接，并与已知的诈骗类型做了比对。",
        "how_layer1": "由我们的本地模型检查。没有发现可疑迹象，所以没有发送到其他地方。",
        "safe_expl": "没有发现可疑迹象，这看起来是一条正常短信。",
        "risky_expl": "我们的模型认为这可能是诈骗。不要点击任何链接。请通过官方网站或卡背面的电话联系该公司。",
        "inconclusive": "这条短信没能检查完。请小心：不要点击链接，并通过官方网站联系该公司。",
        "cap_note": "今天的检查次数已用完，所以只使用了我们的本地模型。",
        "no_key_note": "Claude 智能助手未连接，所以只使用了我们的本地模型。",
        "empty": "请先粘贴一条短信，再点“检查这条短信”。",
        "disclaimer": "SecondLook 是学生做的原型，不构成理财建议。请只粘贴您有权分享的短信。",
    },
}

_CJK = re.compile(r"[一-鿿]")
_ES = re.compile(r"[¿¡ñáéíóú]|\b(el|la|los|las|de|que|por|para|usted|su|es|está|una?)\b", re.I)


def guess_language(text: str) -> str:
    """Cheap guess (en/es/zh), only used to decide whether a translation is needed."""
    if len(_CJK.findall(text)) >= 2:
        return "zh"
    if len(_ES.findall(text)) >= 2:
        return "es"
    return "en"
