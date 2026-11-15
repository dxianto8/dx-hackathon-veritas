# SecondLook: look twice before you tap
A multilingual scam-text checker, made as a phone app.
**Track:** Finance
**Team:** _names_

> This project is a prototype and is not financial advice.

## The problem
Scam texts cost Americans $470 million in 2024 ([FTC](https://www.ftc.gov/news-events/news/press-releases/2025/04/new-ftc-data-show-top-text-message-scams-2024-overall-losses-text-scams-hit-470-million)), and scammers write to immigrant families in their home language, too: the FBI and FCC warn about scams aimed specifically at Chinese speakers in the US. Our user is an **immigrant grandparent** who gets texts in English and in Spanish or Chinese. When a strange text arrives with a link, they want to know "is this safe?" *before* tapping it. Most spam filters are trained on old English data and have never seen a 2026 toll scam written in Spanish or Chinese.

## What we built
**SecondLook** is a phone-friendly web app that installs on the home screen. You choose your language (English, Español or 中文) and paste a text message. You get back:
- a verdict stamp: **SCAM / BE CAREFUL / SAFE** (ESTAFA / CUIDADO / SEGURO, 诈骗 / 小心 / 安全)
- a 2–3 sentence explanation **in your language**, so you learn to spot the trick yourself
- the warning signs it found
- **a translation of the message into your language** if it was written in another one. A grandmother who reads Spanish can understand an English toll scam, and why it's fake.

It works in two layers:
1. **Layer 1 (our trained model):** runs locally, is free, and checks every message.
2. **Layer 2 (Claude agent):** investigates only the messages Layer 1 is unsure about or flags, plus any message where our tools spot a warning sign. It calls two tools we wrote: a **link inspector** (lookalike domains such as `paypa1-support.com`, brand names on unofficial domains such as `usps-redelivery.top`, link shorteners, risky domain endings, raw IP addresses, punycode) and a **scam-pattern matcher** built from FTC, FCC and FBI warnings, with keywords in English, Spanish and Chinese.

## What we added
We started from the suggested **Scam text filter** project (4.2.1) and added:
- **Our own question:** does a filter trained on English spam from 2012 still catch 2026 scams in other languages?
- **Our own data:** *Scams 2026*, a 120-message test set (English, Spanish, Chinese; 20 scam + 20 normal messages each). Every scam is modelled on a type described in a cited FTC, FCC or FBI warning. The normal messages include hard cases such as real bank alerts, real verification codes and real carrier tracking links.
- **Our own user:** a multilingual grandparent, with explanations written in their language.
- **A two-layer design with an AI agent**, and a measurement of what the agent adds and what it costs.

## How it works
**Data**
- Training: [SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), 5,574 English messages (13% spam). Stratified 80/20 split; the 20% validation part is used only to choose the routing threshold.
- Testing: `data/scams2026.csv`. It was never used for training or tuning. The `source_url` column gives the public warning behind each scam, and `data/build_scams2026.py` rebuilds the file.

**Models**
- Baseline 1: always answer "not scam".
- Baseline 2: TF-IDF + logistic regression, the brief's suggested model.
- Layer 1: [`paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) sentence embeddings (50+ languages) + logistic regression. We chose it because it trains in about a minute on a laptop CPU and represents a Spanish or Chinese sentence close to its English meaning, so a model trained only on English can transfer.
- Routing: a message goes to the agent if the Layer 1 probability is at least 0.607 (chosen so that 97% of English validation scams are sent on) **or** our tools find a warning sign.
- Layer 2: Claude Opus 5.5 through the Anthropic API tool runner, at low effort. It must finish by calling a `submit_verdict` tool. If it doesn't (for example, after a refusal), we return "suspicious, inconclusive" rather than crashing.

## Results
Results on the held-out *Scams 2026* test set. "Suspicious" counts as flagged. Recall is the share of scams caught; false alarms are normal messages wrongly flagged.

| System | Lang | Scams caught | Missed scams | False alarms | Precision | F1 |
|---|---|---|---|---|---|---|
| Always "not scam" | all | 0/60 | 60 | 0/60 | – | 0.00 |
| TF-IDF + LR (English-trained) | en | 11/20 | 9 | 6/20 | 0.65 | 0.59 |
| | es | **1/20** | 19 | 0/20 | 1.00 | 0.10 |
| | zh | **1/20** | 19 | 2/20 | 0.33 | 0.09 |
| Layer 1 (multilingual embeddings) | en | 16/20 | 4 | 5/20 | 0.76 | 0.78 |
| | es | 14/20 | 6 | 3/20 | 0.82 | 0.76 |
| | zh | 15/20 | 5 | 4/20 | 0.79 | 0.77 |
| **Two layers (our system)** | en | **19/20** | 1 | **0/20** | 1.00 | **0.97** |
| | es | **19/20** | 1 | **0/20** | 1.00 | **0.97** |
| | zh | **19/20** | 1 | 1/20 | 0.95 | **0.95** |
| Claude agent on every message | en | 20/20 | 0 | 0/20 | 1.00 | 1.00 |
| | es | 19/20 | 1 | 0/20 | 1.00 | 0.97 |
| | zh | 19/20 | 1 | 1/20 | 0.95 | 0.95 |

| System | Claude API calls (of 120) | Cost for 120 messages |
|---|---|---|
| Two layers (our system) | 73 | $2.84 |
| Two layers, routing by Layer 1 threshold only | 51 | $2.00, but catches only 40/60 scams |
| Claude agent on every message | 120 | $4.39 |

**Key findings**
1. **The word-based filter collapses outside English.** It catches 1 in 20 Spanish or Chinese scams, because those words never appear in its English training data.
2. **Multilingual embeddings transfer.** With the same English-only training data, Layer 1 catches 70–80% of scams in all three languages.
3. **A threshold tuned on English doesn't transfer perfectly.** Routing by Layer 1's probability alone sends only 65–70% of the 2026 scams to the agent. Adding our tools' warning signs to the routing raises that to **95% in every language** (57/60). The cost is that 16 of 60 normal messages also get a (cheap) agent check.
4. **The agent turns "flagged" into "right".** Layer 1 alone raised 12 false alarms on 60 normal messages. The agent cleared all but one of them, and it called every one of the 57 scams it received a scam. Overall, the two-layer system catches 57/60 scams with 1 false alarm (F1 0.95–0.97 in every language).
5. **Two layers are nearly as good as Claude on everything, for 35% less.** Claude checking all 120 messages catches one more scam (58 vs 57) but costs $4.39 instead of $2.84. With two layers, 47 of 120 messages are never sent to an outside AI company (Layer 1 runs on our own computer or server), which also matters for privacy.

Full tables: `results/summary.md`. Every prediction: `results/predictions.csv`.

**Where it fails, and why**
- **All 3 missed scams are "wrong number" openers** ("Hi Mark, are we still on for coffee tomorrow? It's Jessica from yoga"). They contain nothing suspicious: no link, no money, no urgency. They are just the first step of a scam that builds trust over weeks ([FTC](https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/04/top-text-scams-2024)). Layer 1 gave them a 1–17% scam probability, so they never reached the agent.
- **The agent judged the same message differently by language.** When we sent the "wrong number" message to Claude in all three languages (agent-on-everything run), it said **"suspicious" in English** but **"safe" in Spanish and Chinese**. All three explanations mention the wrong-number trick, but only the English verdict acted on it. This is one message per language, so it's a lead rather than proof, but it suggests non-English speakers could get weaker protection, which is exactly the gap this project is about. A fix to test next: tell the agent to rate any message from an unknown sender that starts a conversation as "suspicious".
- **The 1 false alarm:** a real Google verification code with a Chinese warning line (`Your Google verification code is 731052. 请勿将验证码告诉任何人。`). Layer 1 gave it 0.91, perhaps because of the mixed languages and the number, and the agent said "suspicious". Its explanation is still sensible: "if you didn't request this code, someone may be trying to log in to your account."
- **Real company messages look like scams.** Genuine UPS or Amazon delivery texts match the "package" scam pattern. The agent handled them correctly: the link goes to the official domain and nothing is being asked for.
- See `results/failures.csv` for each mistake.

**Honest limits:** the test set is small (120 messages), and its messages were drafted with an AI assistant from public warnings rather than collected from real phones. They still need checking by native speakers (see "What we'd do next").

## What we'd do next
1. Replace the AI-drafted test messages with real ones quoted in public warnings and scam-report sites. Have native Spanish and Chinese speakers on the team check every label and rate the agent's explanations.
2. Test with a real grandparent: is the explanation clear, and what would they do next?
3. A native Android app that lets you *share* a text straight from the messages app into SecondLook, so there's no copying and pasting.

## The app
- **Phone:** open the app link on a phone and choose *Add to Home Screen* (iPhone: Share button; Android: browser menu). It then opens full-screen with its own icon.
- **Spending cap:** every Claude call is counted, and once a day's limit is reached (default $3, set with `DAILY_LIMIT_USD`), the app answers with Layer 1 only and says so. A public link can't drain the API credit.
- **Design for older eyes:** it uses the Atkinson Hyperlegible typeface (made for low-vision readers) at an 18px base size, a stamp you can read at a glance, and high-contrast colours.
- Note: the results above were measured with explanations in the message's own language. The "explain in your language" and translation features were added to the app afterwards and haven't been through the same evaluation yet.

## Deploy it (free, Hugging Face Spaces)
1. `python scripts/build_hf_space.py` builds `dist/hf_space/`.
2. At huggingface.co, go to **New Space**, choose the **Gradio** SDK and the free **CPU basic** hardware, then upload everything inside `dist/hf_space/`.
3. In the Space's **Settings → Variables and secrets**, add the secret `ANTHROPIC_API_KEY`. Never put a key in a file.
4. Wait for the build (a few minutes), then open the Space link on your phone and add it to the home screen.

## How to run
```bash
pip install -r requirements.txt
python scripts/train_layer1.py           # ~2 min on CPU
python -m pytest -q                      # 35 tests, no API calls
python scripts/evaluate.py               # free part of the evaluation
export ANTHROPIC_API_KEY=...             # never commit your key
python scripts/evaluate.py --agent       # two-layer system (we paid $2.84)
python scripts/evaluate.py --agent --agent-only   # both systems (we paid $4.39 in total)
python app.py                            # SecondLook at http://127.0.0.1:7860
```
Agent answers are cached in `results/agent_cache.jsonl`, so reruns are free. Spending stops at `--budget` dollars (default $10).

## Sources
- Data: [SMS Spam Collection (UCI)](https://archive.ics.uci.edu/dataset/228/sms+spam+collection). Scam types: [FTC top text scams 2024](https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/04/top-text-scams-2024), [FTC unpaid tolls](https://consumer.ftc.gov/consumer-alerts/2025/01/got-text-about-unpaid-tolls-its-probably-scam), [FCC toll scams](https://www.fcc.gov/consumer-governmental-affairs/how-spot-and-avoid-toll-road-payment-scam-texts), [FCC package delivery scams](https://www.fcc.gov/how-identify-and-avoid-package-delivery-scams), [FTC task scams](https://consumer.ftc.gov/consumer-alerts/2025/08/how-spot-avoid-task-scams), [FTC job-offer texts 2026](https://consumer.ftc.gov/consumer-alerts/2026/04/job-offer-text-probably-scam) ([español](https://consumidor.ftc.gov/alertas-para-consumidores/2026/04/es-probable-que-ese-mensaje-de-texto-con-una-propuesta-de-trabajo-sea-una-estafa)), [FCC scam glossary](https://www.fcc.gov/scam-glossary), [FBI: Chinese police imposters](https://www.fbi.gov/investigate/cyber/alerts/2024/chinese-police-imposters-incorporate-aggressive-tactics-to-target-us-based-chinese-community), [FBI: health-insurance impersonation](https://www.fbi.gov/investigate/cyber/alerts/2025/criminals-impersonate-us-health-insurance-providers-and-chinese-law-enforcement-to-target-chinese-speakers-residing-in-the-united-states), [FCC: scams targeting Chinese-Americans](https://www.fcc.gov/chinese-language-robocall-scams), [FTC: Chinese consulate impersonation](https://consumer.ftc.gov/consumer-alerts/2018/04/scammers-impersonate-chinese-consulate).
- Models and libraries: [paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2), [sentence-transformers](https://www.sbert.net/), [scikit-learn](https://scikit-learn.org/), [Anthropic Claude API](https://docs.claude.com/) (Claude Opus 5.5), [Gradio](https://www.gradio.app/), pandas, [Atkinson Hyperlegible](https://www.brailleinstitute.org/freefont/) and [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) typefaces.
- AI tools: Claude (Anthropic) via Claude Code helped design the project, write code, and draft the test messages from the cited warnings.
