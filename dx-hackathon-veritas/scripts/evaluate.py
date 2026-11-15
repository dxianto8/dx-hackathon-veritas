"""Evaluate every system on the Scams 2026 test set, per language.

  python scripts/evaluate.py                 # free: baselines + Layer 1 + routing stats
  python scripts/evaluate.py --agent         # + two-layer system (calls Claude; needs ANTHROPIC_API_KEY)
  python scripts/evaluate.py --agent-only    # + Claude agent on every message (comparison)

'suspicious' counts as flagged. Agent answers are cached in results/agent_cache.jsonl,
so reruns are free. Spending stops at --budget dollars (default 10).
"""
import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scamcheck.agent import check_with_agent  # noqa: E402
from scamcheck.data import load_scams2026  # noqa: E402
from scamcheck.pipeline import _layer1, should_route, tool_signals  # noqa: E402

RESULTS = ROOT / "results"
CACHE = RESULTS / "agent_cache.jsonl"


class AgentCache:
    def __init__(self, budget):
        self.budget, self.spent, self.data = budget, 0.0, {}
        if CACHE.exists():
            for line in CACHE.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                self.data[r["text"]] = r
        self.client = None

    def get(self, text, p):
        if text in self.data:
            return self.data[text]
        if self.spent >= self.budget:
            return None
        import anthropic
        self.client = self.client or anthropic.Anthropic()
        v = asdict(check_with_agent(text, p, client=self.client))
        v["text"] = text
        self.spent += v["cost_usd"]
        self.data[text] = v
        with CACHE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
        print(f"  agent: {v['verdict']:<10} ${self.spent:.3f} so far | {text[:50]}")
        return v


def metrics(g, col, cost_col=None):
    pred, y = g[col].astype(int), g.y
    tp, fn = int(((pred == 1) & (y == 1)).sum()), int(((pred == 0) & (y == 1)).sum())
    fp, tn = int(((pred == 1) & (y == 0)).sum()), int(((pred == 0) & (y == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    out = {"scams_caught": f"{tp}/{tp + fn}", "recall": round(rec, 2), "missed_scams": fn,
           "false_alarms": f"{fp}/{fp + tn}", "precision": round(prec, 2), "f1": round(f1, 2)}
    if cost_col:
        out["api_calls"] = int(g[cost_col].notna().sum())
        out["cost_usd"] = round(float(g[cost_col].fillna(0).sum()), 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", action="store_true")
    ap.add_argument("--agent-only", action="store_true")
    ap.add_argument("--budget", type=float, default=10.0)
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)

    d = load_scams2026()
    d["p_layer1"] = _layer1().predict_proba(d.text)
    d["p_tfidf"] = joblib.load(ROOT / "models/tfidf.joblib").predict_proba(d.text)[:, 1]
    d["signals"] = d.text.map(tool_signals)
    d["routed_threshold"] = [should_route(p, s, "threshold") for p, s in zip(d.p_layer1, d.signals)]
    d["routed_signals"] = [should_route(p, s, "signals") for p, s in zip(d.p_layer1, d.signals)]

    systems = {
        "Always 'not scam' (baseline)": ("pred_majority", None),
        "TF-IDF + LR, English-trained (baseline)": ("pred_tfidf", None),
        "Layer 1: multilingual embeddings + LR": ("pred_layer1", None),
        "Upper bound: share of scams that reach agent (threshold routing)": ("routed_threshold", None),
        "Upper bound: share of scams that reach agent (threshold + tool-signal routing)": ("routed_signals", None),
    }
    d["pred_majority"] = 0
    d["pred_tfidf"] = (d.p_tfidf >= 0.5).astype(int)
    d["pred_layer1"] = (d.p_layer1 >= 0.5).astype(int)

    if args.agent or args.agent_only:
        cache = AgentCache(args.budget)
        agent_v = {}
        for t, p, rs, rt in zip(d.text, d.p_layer1, d.routed_signals, d.routed_threshold):
            if args.agent_only or rs or rt:
                agent_v[t] = cache.get(t, p)
        def flagged(t):
            v = agent_v.get(t)
            return None if v is None else int(v["verdict"] in ("scam", "suspicious"))
        def cost(t):
            v = agent_v.get(t)
            return None if v is None else v["cost_usd"]
        for route in ("threshold", "signals"):
            col = f"routed_{route}"
            d[f"pred_two_layer_{route}"] = [flagged(t) if r else 0 for t, r in zip(d.text, d[col])]
            d[f"cost_two_layer_{route}"] = [cost(t) if r else None for t, r in zip(d.text, d[col])]
        systems["Two layers (threshold routing)"] = ("pred_two_layer_threshold", "cost_two_layer_threshold")
        systems["Two layers (threshold + tool-signal routing) - OUR SYSTEM"] = ("pred_two_layer_signals", "cost_two_layer_signals")
        if args.agent_only:
            d["pred_agent_only"] = d.text.map(flagged)
            d["cost_agent_only"] = d.text.map(cost)
            systems["Claude agent on every message"] = ("pred_agent_only", "cost_agent_only")
        d["agent_verdict"] = d.text.map(lambda t: (agent_v.get(t) or {}).get("verdict"))
        d["agent_explanation"] = d.text.map(lambda t: (agent_v.get(t) or {}).get("explanation"))
        missing = sum(v is None for v in agent_v.values())
        if missing:
            print(f"WARNING: budget reached, {missing} messages have no agent verdict; they are excluded.")

    rows = []
    for name, (col, cost_col) in systems.items():
        dd = d[d[col].notna()]
        for lang, g in [("ALL", dd)] + list(dd.groupby("language")):
            rows.append({"system": name, "language": lang, **metrics(g, col, cost_col)})
    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / "metrics.csv", index=False)
    d.drop(columns=["signals"]).assign(signals=d.signals.map("; ".join)).to_csv(
        RESULTS / "predictions.csv", index=False, encoding="utf-8")

    main_col = "pred_two_layer_signals" if "pred_two_layer_signals" in d else "pred_layer1"
    errs = d[d[main_col].notna() & (d[main_col] != d.y)]
    cols = ["language", "label", "scam_type", "text", "p_layer1"] + (["agent_verdict", "agent_explanation"] if "agent_verdict" in d else [])
    errs[cols].to_csv(RESULTS / "failures.csv", index=False, encoding="utf-8")

    with open(RESULTS / "summary.md", "w", encoding="utf-8") as f:
        f.write("# Results on Scams 2026 (held-out, never used for training or thresholds)\n\n")
        f.write(table.to_markdown(index=False) + "\n\n")
        f.write(f"## Mistakes made by: {main_col}\n\n")
        f.write(errs[cols].to_markdown(index=False) + "\n")
    print(table.to_string(index=False))
    print(f"\nWrote {RESULTS}/metrics.csv, predictions.csv, failures.csv, summary.md")


if __name__ == "__main__":
    main()
