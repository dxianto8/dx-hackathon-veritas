"""Build a folder you can upload to a Hugging Face Space.

  python scripts/build_hf_space.py      ->  dist/hf_space/
Then upload everything inside dist/hf_space/ to your Space, and add the secret ANTHROPIC_API_KEY.
"""
import shutil
from pathlib import Path

import gradio

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "hf_space"

FRONT_MATTER = f"""---
title: SecondLook
emoji: 🔍
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: {gradio.__version__}
app_file: app.py
pinned: false
short_description: Look twice before you tap. A multilingual scam-text checker.
---

# SecondLook

Paste a text message and SecondLook tells you whether it looks like a scam, and why, in English, Spanish or Chinese.
A student prototype for the Veritas AI High School Hackathon 2026. This project is a prototype and is not financial advice.

Needs the Space secret `ANTHROPIC_API_KEY`. Optional variable `DAILY_LIMIT_USD` (default 3) caps daily Claude spending.
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copy(ROOT / "app.py", OUT)
    for d in ["scamcheck", "models", "assets"]:
        shutil.copytree(ROOT / d, OUT / d, ignore=shutil.ignore_patterns("__pycache__"))
    (OUT / "data").mkdir()
    for f in ["brand_domains.json", "known_patterns.json"]:
        shutil.copy(ROOT / "data" / f, OUT / "data")
    reqs = [l for l in (ROOT / "requirements.txt").read_text().splitlines() if l and not l.startswith(("pytest", "tabulate", "gradio"))]
    (OUT / "requirements.txt").write_text("\n".join(reqs) + "\n")
    (OUT / "README.md").write_text(FRONT_MATTER, encoding="utf-8")
    print(f"Built {OUT}")
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print("  ", p.relative_to(OUT))


if __name__ == "__main__":
    main()
