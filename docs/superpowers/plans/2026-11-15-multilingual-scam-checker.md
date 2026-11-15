# Multilingual Scam Checker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Two-layer scam-text checker (multilingual embeddings + LR, then a Claude agent) with a cited multilingual 2026 test set and a per-language evaluation.

**Architecture:** `scamcheck/layer1.py` trains/loads the embedding classifier; `scamcheck/tools.py` holds pure-Python investigation tools; `scamcheck/agent.py` runs the Claude tool runner; `scamcheck/pipeline.py` routes between layers; `scripts/evaluate.py` produces all result tables; `app.py` is the Gradio demo.

**Tech Stack:** Python 3.10+, sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`), scikit-learn, pandas, anthropic SDK (tool runner, `claude-opus-5-5`), gradio, pytest.

**Spec:** `docs/superpowers/specs/2026-11-15-multilingual-scam-checker-design.md`

## Global Constraints

- Languages: English (`en`), Spanish (`es`), Chinese Simplified (`zh`) — default until the team names its languages.
- Test data public or team-written only; every row has `source_url`. AI-drafted rows marked `origin=ai_written` for team review.
- API key only from `ANTHROPIC_API_KEY`; never written to disk.
- Evaluation API spend cap: $10 (script estimates cost and stops at cap).
- README contains: "This project is a prototype and is not financial advice."
- No test-set rows used for training or threshold choice.

## Review Focus

- Message with no links → `analyze_links` returns empty findings, agent still answers.
- Agent never calls `submit_verdict` → pipeline returns `suspicious` with an explanation saying the check was inconclusive (never crashes).
- No API key → pipeline falls back to Layer 1 only and says so.
- Non-ASCII / punycode domains (`xn--`) → flagged.
- Empty or whitespace-only input in the demo → friendly error, no API call.

---

### Task 1: Data — SMS loader and Scams 2026 test set

**Files:** Create `scamcheck/data.py`, `data/scams2026.csv`, `data/known_patterns.json`, `data/brand_domains.json`; Test `tests/test_data.py`

**Interfaces:** Produces `load_sms(path) -> pd.DataFrame[text,label]` (label 1=scam), `load_scams2026(path) -> pd.DataFrame[text,label,language,scam_type,origin,source_url,notes]`.

- [ ] Test: `load_sms` returns 5574 rows, labels in {0,1}, ~13% positive; `load_scams2026` has every `source_url` non-empty, `language` ⊂ {en,es,zh}, ≥15 scam and ≥15 legit per language.
- [ ] Implement, run tests, commit.

### Task 2: Investigation tools

**Files:** Create `scamcheck/tools.py`; Test `tests/test_tools.py`

**Interfaces:** Produces `analyze_links_impl(text: str) -> dict` (`{"links": [ {url, domain, flags[]} ], "summary": str}`), `match_known_patterns_impl(text: str) -> dict` (`{"matches": [{pattern_id, name, score, source_url}]}`).

- [ ] Tests: `paypa1.com` flagged `lookalike:paypal.com`; `bit.ly/x` flagged `shortener`; `http://192.168.1.1/a` flagged `ip_address`; `xn--pple-43d.com` flagged `punycode`; `usps.com` not flagged; no-link text → empty list; toll text matches `toll_fee`; Chinese consulate text matches `authority_impersonation`.
- [ ] Implement (edit distance ≤2 to brand second-level label; keyword-overlap scoring for patterns, multilingual keywords in JSON); run; commit.

### Task 3: Layer 1 classifier + TF-IDF baseline

**Files:** Create `scamcheck/layer1.py`; Test `tests/test_layer1.py`

**Interfaces:** Produces `class Layer1: fit(texts, labels); predict_proba(texts) -> np.ndarray; save(path); load(path)`, `train_tfidf_baseline(texts, labels) -> sklearn Pipeline`, `choose_low_threshold(probs, labels, target_recall=0.97) -> float`.

- [ ] Tests: fit on 8 toy messages → scam prob of "WIN cash prize claim now" > prob of "see you at dinner"; `choose_low_threshold` returns threshold where recall ≥ target on given arrays.
- [ ] Implement; train script `scripts/train_layer1.py` saves `models/layer1.joblib` and `models/threshold.json` using SMS validation split (stratified 80/20, seed 42); run; commit.

### Task 4: Claude agent

**Files:** Create `scamcheck/agent.py`; Test `tests/test_agent.py`

**Interfaces:** Consumes Task 2 impls. Produces `@dataclass Verdict(verdict, confidence, language, explanation, red_flags, layer, cost_usd)`; `check_with_agent(text, layer1_prob, client=None) -> Verdict`.

- [ ] Tests (fake client injected, no network): when fake runner calls `submit_verdict`, returned Verdict matches; when it never does → verdict `suspicious`, explanation mentions inconclusive.
- [ ] Implement with `client.beta.messages.tool_runner(model="claude-opus-5-5", output_config={"effort":"low"}, betas=["server-side-fallback-2026-07-01"], fallbacks="default", tools=[analyze_links, match_known_patterns, submit_verdict])`; retry once without fallbacks on `BadRequestError`; cost from usage at $4/$20 per MTok; run; commit.

### Task 5: Pipeline + evaluation

**Files:** Create `scamcheck/pipeline.py`, `scripts/evaluate.py`; Test `tests/test_pipeline.py`

**Interfaces:** Produces `check_message(text, use_agent=True) -> Verdict`; `evaluate.py` writes `results/*.csv` + `results/summary.md`.

- [ ] Tests: prob < threshold → layer1 `safe` without agent call; no key → layer1-only verdict with note.
- [ ] Evaluate systems: majority, TF-IDF, Layer1, Layer1+agent (`--agent`), agent-only (`--agent-only`), per language: recall, false alarms, precision, F1, API calls, $; failure examples; cost cap. Run non-agent part here; commit.

### Task 6: Demo + write-up

**Files:** Create `app.py`, `README.md`, `requirements.txt`

- [ ] Gradio: textbox → verdict, confidence, explanation, red flags, layer; empty input → error message.
- [ ] README in hackathon template with results tables, disclaimer, credits; commit.
