"""SecondLook: a multilingual scam-text checker.  Run: python app.py"""
import html
import os
from pathlib import Path

import gradio as gr

from scamcheck.budget import DailyBudget
from scamcheck.i18n import LANGS, T
from scamcheck.pipeline import check_message

ROOT = Path(__file__).resolve().parent
DAILY_LIMIT_USD = float(os.environ.get("DAILY_LIMIT_USD", "3"))
BUDGET = DailyBudget(ROOT / "usage" / "spend.json", DAILY_LIMIT_USD)

EXAMPLES = [
    "E-ZPass: You have an unpaid toll balance of $4.35. To avoid a $50 late fee, pay now: https://ezpass-tollpay.top/pay",
    "Hola, Walmart está contratando evaluadores en línea. Trabajo desde casa, $250 al día. Responda SÍ si le interesa.",
    "【中国驻芝加哥总领事馆】您有一份重要文件待领取，涉及您的护照问题。请立即回电 1-312-555-0166 按9转人工。",
    "Mom, can you pick me up from practice at 6:30?",
]

HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
<meta name="theme-color" content="#1F2A44">
<script>
  // SecondLook is designed for a light page; keep it readable when the phone is in dark mode.
  const u = new URL(window.location.href);
  if (u.searchParams.get("__theme") !== "light") { u.searchParams.set("__theme", "light"); window.location.replace(u); }
</script>
"""

CSS = """
:root { --ink:#1F2A44; --paper:#F6F8FB; --rule:#D5DAE3; --scam:#C62828; --careful:#A15C00; --safe:#2E7D32; --muted:#55607A; }
body, .gradio-container { background: var(--paper) !important; }
.gradio-container { --color-accent: #1F2A44; --color-accent-soft: #E3E8F2; --checkbox-background-color-selected: #1F2A44;
  --checkbox-border-color-selected: #1F2A44; --checkbox-border-color-focus: #1F2A44; --checkbox-label-background-fill-selected: #E3E8F2; }
#lang input[type=radio] { accent-color: #1F2A44; }
.gradio-container, .gradio-container * :not(code) {
  font-family: "Atkinson Hyperlegible", "Noto Sans SC", system-ui, sans-serif !important;
}
.gradio-container { max-width: 640px !important; margin: 0 auto !important; padding: 20px 16px 48px !important;
  color: var(--ink); font-size: 18px; }
footer { display: none !important; }
.sl-head h1 { font-size: 2.6rem; line-height: 1.05; margin: 8px 0 4px; font-weight: 700; color: var(--ink); letter-spacing: -0.01em; }
.sl-head h1 .two { color: var(--scam); }
.sl-head .tag { font-size: 1.25rem; margin: 0 0 10px; color: var(--ink); }
.sl-head .intro { font-size: 1.05rem; line-height: 1.5; color: var(--muted); margin: 0; }
#msg textarea { font-size: 1.1rem !important; line-height: 1.5 !important; border: 2px solid var(--rule) !important;
  border-radius: 10px !important; background: #fff !important; color: var(--ink) !important; }
#msg textarea:focus { border-color: var(--ink) !important; outline: 3px solid #9DB3E0; outline-offset: 1px; }
#check { background: var(--ink) !important; color: #fff !important; font-size: 1.2rem !important; font-weight: 700 !important;
  min-height: 56px; border-radius: 10px !important; border: none !important; }
#check:hover { background: #2C3A5C !important; }
#check:focus-visible { outline: 3px solid #9DB3E0; outline-offset: 2px; }
#lang label span, #msg label span { font-size: 1rem !important; color: var(--ink) !important; font-weight: 700 !important; }
.sl-card { background: #fff; border: 2px solid var(--rule); border-radius: 12px; padding: 22px 20px 18px; color: var(--ink); }
.sl-card.scam { border-color: var(--scam); } .sl-card.suspicious { border-color: var(--careful); } .sl-card.safe { border-color: var(--safe); }
.stamp { display: inline-block; font-weight: 700; font-size: 2.3rem; line-height: 1; letter-spacing: 0.04em;
  padding: 10px 18px 8px; border: 4px solid currentColor; border-radius: 8px; transform: rotate(-4deg);
  box-shadow: inset 0 0 0 3px #fff, inset 0 0 0 5px currentColor; margin: 4px 0 18px 4px;
  animation: stamp-in 260ms cubic-bezier(.2,1.6,.4,1) both; }
.stamp.scam { color: var(--scam); } .stamp.suspicious { color: var(--careful); } .stamp.safe { color: var(--safe); }
@keyframes stamp-in { from { transform: rotate(-4deg) scale(1.6); opacity: 0; } to { transform: rotate(-4deg) scale(1); opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .stamp { animation: none; } }
.sl-card .expl { font-size: 1.2rem; line-height: 1.55; margin: 0 0 16px; }
.sl-card h3 { font-size: 1rem; margin: 18px 0 6px; color: var(--ink); font-weight: 700; }
.sl-card ul { margin: 0; padding-left: 1.2em; line-height: 1.6; }
.sl-card .translation { background: var(--paper); border-left: 4px solid var(--ink); padding: 10px 14px; margin: 0;
  line-height: 1.55; white-space: pre-wrap; }
.sl-card .how { font-size: 0.9rem; color: var(--muted); margin: 18px 0 0; line-height: 1.45; }
.sl-empty { color: var(--muted); font-size: 1.05rem; padding: 6px 2px; }
.sl-foot { font-size: 0.9rem; color: var(--muted); line-height: 1.45; margin-top: 8px; }
"""


def lang_code(choice: str) -> str:
    return LANGS.get(choice, "en")


def header_html(code: str) -> str:
    ui = T[code]
    return (f'<div class="sl-head"><h1>Second<span class="two">Look</span></h1>'
            f'<p class="tag">{html.escape(ui["tagline"])}</p><p class="intro">{html.escape(ui["intro"])}</p></div>')


def footer_html(code: str) -> str:
    return f'<p class="sl-foot">{html.escape(T[code]["disclaimer"])}</p>'


def result_html(text: str, choice: str) -> str:
    code = lang_code(choice)
    ui = T[code]
    try:
        v = check_message(text, reply_lang=code, budget=BUDGET)
    except ValueError as e:
        return f'<p class="sl-empty">{html.escape(str(e))}</p>'
    verdict = v.verdict if v.verdict in ui["stamp"] else "suspicious"
    parts = [f'<div class="sl-card {verdict}" role="status" aria-live="polite">',
             f'<div class="stamp {verdict}">{html.escape(ui["stamp"][verdict])}</div>',
             f'<p class="expl">{html.escape(v.explanation)}</p>']
    if v.red_flags:
        items = "".join(f"<li>{html.escape(str(f))}</li>" for f in v.red_flags)
        parts.append(f'<h3>{html.escape(ui["signs"])}</h3><ul>{items}</ul>')
    if v.translation:
        parts.append(f'<h3>{html.escape(ui["translation"])}</h3><p class="translation">{html.escape(v.translation)}</p>')
    how = ui["how_agent"] if v.layer == "agent" else ui["how_layer1"] if v.verdict == "safe" else ""
    extra = f" {v.note}" if v.note and v.note != "agent gave no verdict" else ""
    if how or extra:
        parts.append(f'<p class="how">{html.escape((how + extra).strip())}</p>')
    parts.append("</div>")
    return "".join(parts)


def relabel(choice: str):
    code = lang_code(choice)
    ui = T[code]
    return (header_html(code), gr.update(label=ui["lang_label"]),
            gr.update(label=ui["box_label"], placeholder=ui["box_placeholder"]),
            gr.update(value=ui["button"]), footer_html(code))


with gr.Blocks(title="SecondLook") as demo:
    header = gr.HTML(header_html("en"))
    lang = gr.Radio(list(LANGS), value="English", label=T["en"]["lang_label"], elem_id="lang")
    box = gr.Textbox(lines=5, label=T["en"]["box_label"], placeholder=T["en"]["box_placeholder"], elem_id="msg")
    btn = gr.Button(T["en"]["button"], elem_id="check")
    result = gr.HTML()
    gr.Examples(EXAMPLES, inputs=box, label="Try an example / Pruebe un ejemplo / 试一个例子")
    footer = gr.HTML(footer_html("en"))

    btn.click(result_html, [box, lang], result)
    lang.change(relabel, lang, [header, lang, box, btn, footer])

if __name__ == "__main__":
    # pwa=True makes it installable ("Add to Home Screen"). Host/port come from GRADIO_SERVER_NAME/PORT if set.
    demo.launch(css=CSS, head=HEAD, favicon_path=str(ROOT / "assets" / "icon.png"), pwa=True)
