# Multilingual Scam Text Checker — Design

**Hackathon:** Veritas AI International High School Hackathon 2026
**Track:** AI + Finance (scam text filter, extended)
**Deadline:** Sun Nov 15, 11:59 PM ET (10:59 PM Chicago)

## Intent and why

Scammers text people in their home language as well as English. The classic
SMS Spam Collection (English, ~2012) is what most spam filters are taught on.
Our question: **does a filter trained on old English spam catch today's scams
in other languages, and does adding an investigating Claude agent close the
gap?**

**User:** an immigrant grandparent (or international student) in the US who
receives scam texts in English and in their home language. The moment of use:
they get a strange text with a link and want to know "is this safe?" before
tapping it. The tool answers with a verdict and a short explanation *in the
message's own language*, so they learn to spot the pattern themselves.

## Goals

- A two-layer checker:
  1. **Layer 1 – trained model (ours):** multilingual sentence embeddings +
     logistic regression, trained only on the English SMS Spam Collection.
     Runs locally, free, fast.
  2. **Layer 2 – Claude agent:** messages that Layer 1 is unsure about or flags
     go to an agent that investigates with our own tools and explains its
     verdict in the message's language.
- A new **2026 multilingual scam test set** we build ourselves from public
  sources, with every row cited.
- An honest evaluation, broken down **per language**, reporting missed scams
  (false negatives) and false alarms (false positives) separately, plus API
  cost per message.
- A Gradio demo: paste a text → verdict, confidence, explanation, which layer
  decided.
- Write-up following the hackathon template, including:
  "This project is a prototype and is not financial advice."

## Non-goals

- Not a phone app or SMS integration.
- Not training a large model from scratch or fine-tuning on a GPU (no GPU here;
  Colab fine-tuning is an optional stretch only).
- Not covering every language — a handful done carefully beats many done badly.

## Anti-goals (would count as failure even if it "works")

- Using anyone's private messages without permission. Test data is public or
  team-written only, and only that is sent to the API.
- Reporting a single overall accuracy number. Judges want per-language,
  per-error-type results.
- Test data leaking into training or threshold tuning.
- Overspending the ~$30 API credit. Hard cap for evaluation runs: **$10**.

## Constraints

- ~27 hours from design approval to deadline; team comfortable with Python.
- Environment: 4 CPUs, 15 GB RAM, no GPU.
- Anthropic API key with ~$30 credit. Model: `claude-opus-5-5` (default).
- Submission needs: public code (this GitHub repo), one-page write-up,
  optional ≤2-minute video, credits for every dataset/model/AI tool used.

## Approaches considered

1. **Two layers: trained model first, Claude agent for uncertain/flagged
   messages — CHOSEN.** Most of our own work, cheap, keeps most messages off
   the API, and gives a clear story: how much do accuracy and cost change
   when the agent is added, per language?
2. **Claude agent only.** Simplest, but least of our own work, and every
   message costs money and leaves the device. Kept as a comparison row if the
   budget allows.
3. **Trained model only, Claude as a comparison.** Strong on "we built it",
   but no explanation for the user.

## Design

### Data

- **Training:** SMS Spam Collection (5,574 English messages, ~13% spam), split
  stratified into train / validation. Validation is used to choose Layer 1
  thresholds.
- **Test — "Scams 2026" (ours):** `data/scams2026.csv` with columns
  `text, label (scam|legit), language, scam_type, origin (collected|written),
  source_url, notes`.
  - Target ~20 scam + ~20 legit messages per language.
  - Scams come from public warnings (government consumer agencies, banks,
    carriers, news articles). If a page describes a scam without quoting the
    text, a team member writes a realistic example from it, marked
    `origin=written`, with the URL cited.
  - Legit messages: realistic everyday texts (delivery notices from real
    carriers' formats, appointment reminders, family chat) written by the team.
    These matter: they produce the false-alarm numbers.
  - **Languages: English + ≥2 others. At least one non-English language must be
    one a team member reads, who checks every label in that language by hand.**
  - The original SMS test split is also reported, as the "old English" reference.

### Layer 1 — trained model

- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (50+ languages,
  runs on CPU) → embeddings → `LogisticRegression(class_weight="balanced")`.
- Output: scam probability *p*. Decision rule:
  - *p* < low threshold → **safe**, no API call
  - otherwise → send to the agent (uncertain zone and flagged messages both get
    the explanation the user needs)
  - Low threshold chosen on the English validation set to keep missed scams
    rare; we report how well that choice transfers to other languages.

### Layer 2 — Claude agent

- Anthropic Python SDK, Tool Runner (`client.beta.messages.tool_runner`), model
  `claude-opus-5-5`, adaptive thinking, low/medium effort, refusal fallback
  enabled.
- Tools (all ours, plain Python, no network needed):
  - `analyze_links(text)` — extract URLs; flag lookalike brand domains
    (edit-distance to a list of real bank/carrier/government domains),
    punycode, URL shorteners, IP-address links, odd TLDs.
  - `match_known_patterns(text)` — compare against our list of 2026 scam
    patterns (toll/parcel fees, "Hi Mum new number", OTP/verification-code
    requests, fake job offers, prize/refund) built from the same public
    sources; returns closest matches.
- Final answer as structured output: `verdict (scam|suspicious|safe)`,
  `confidence`, `language`, `explanation` (2–3 sentences in the message's
  language), `red_flags` (list).
- The prompt also receives Layer 1's probability.

### Evaluation (in a notebook with outputs saved)

Rows compared on the Scams 2026 test set, **per language** and overall:

| System | Notes |
|---|---|
| Always "not scam" | majority baseline |
| TF-IDF + logistic regression (English-trained) | the brief's suggested model |
| Layer 1 alone | our trained model |
| Layer 1 + agent (two layers) | the product |
| Agent alone | only if under budget |

Report for each: scam recall, false alarms, precision, F1, API calls and $ per
100 messages. Show ≥5 failure examples side by side (message, truth, verdict,
explanation) and explain why each failed. Native-speaker check: the team
member rates the agent's explanations in their language (clear / wrong / unclear).

### Repo layout

```
data/           scams2026.csv, known_patterns.json, brand_domains.json
scamcheck/      layer1.py, tools.py, agent.py, pipeline.py
notebooks/      evaluation.ipynb (outputs saved)
app.py          Gradio demo
README.md       write-up (hackathon template) + credits + disclaimer
```

API key read from `ANTHROPIC_API_KEY`; never committed.

## Left to the builder

- Exact threshold values, prompt wording, embedding batch sizes.
- Exact list of brand domains and pattern list contents (sourced and cited).
- Whether to add an optional Colab fine-tune of XLM-RoBERTa (only if time).

## Open question for the team

- Which non-English languages can a team member read and check by hand?
