"""Gradio demo: paste a text message, get a verdict.  Run: python app.py"""
import gradio as gr

from scamcheck.pipeline import check_message

ICON = {"scam": "🚫 SCAM", "suspicious": "⚠️ SUSPICIOUS", "safe": "✅ LOOKS SAFE"}
EXAMPLES = [
    "E-ZPass: You have an unpaid toll balance of $4.35. To avoid a $50 late fee, pay now: https://ezpass-tollpay.top/pay",
    "Hola, Walmart está contratando evaluadores en línea. Trabajo desde casa, $250 al día. Responda SÍ si le interesa.",
    "【中国驻芝加哥总领事馆】您有一份重要文件待领取，涉及您的护照问题。请立即回电 1-312-555-0166 按9转人工。",
    "Your Google verification code is 482913. Don't share this code with anyone.",
    "Mom, can you pick me up from practice at 6:30?",
]


def run(text):
    try:
        v = check_message(text)
    except ValueError as e:
        return f"**{e}**"
    flags = "".join(f"\n- {f}" for f in v.red_flags) or " none"
    who = "Claude agent (investigated)" if v.layer == "agent" else "Layer 1 (local model)"
    lines = [f"## {ICON.get(v.verdict, v.verdict)}", f"**Confidence:** {v.confidence:.0%}", "", v.explanation, "",
             f"**Warning signs:**{flags}", "", f"<sub>Decided by: {who} · Layer 1 scam probability: "
             f"{(v.layer1_prob or 0):.2f} · API cost: ${v.cost_usd:.3f}</sub>"]
    if v.note:
        lines.append(f"<sub>{v.note}</sub>")
    return "\n".join(lines)


demo = gr.Interface(
    fn=run,
    inputs=gr.Textbox(lines=5, label="Paste the text message (English, Español, 中文)"),
    outputs=gr.Markdown(),
    examples=EXAMPLES,
    title="Is this text a scam?",
    description="A prototype scam checker for families who get scam texts in more than one language. "
                "This project is a prototype and is not financial advice. Only paste messages you have permission to share.",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch()
