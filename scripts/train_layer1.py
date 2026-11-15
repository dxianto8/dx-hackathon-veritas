"""Train Layer 1 on the English SMS Spam Collection and pick the routing threshold.

Usage: python scripts/train_layer1.py
Writes models/layer1.joblib, models/tfidf.joblib, models/threshold.json
"""
import json
import sys
from pathlib import Path

import joblib
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scamcheck.data import load_sms  # noqa: E402
from scamcheck.layer1 import Layer1, choose_low_threshold, train_tfidf_baseline  # noqa: E402

TARGET_RECALL = 0.97


def main():
    df = load_sms()
    tr, va = train_test_split(df, test_size=0.2, stratify=df.label, random_state=42)
    (ROOT / "models").mkdir(exist_ok=True)

    model = Layer1().fit(tr.text, tr.label)
    model.save(ROOT / "models/layer1.joblib")
    tfidf = train_tfidf_baseline(tr.text, tr.label)
    joblib.dump(tfidf, ROOT / "models/tfidf.joblib")

    p = model.predict_proba(va.text)
    thr = choose_low_threshold(p, va.label.values, TARGET_RECALL)
    print("Layer 1 on SMS validation (threshold 0.5):")
    print(classification_report(va.label, p >= 0.5, target_names=["legit", "spam"], digits=3))
    sent = (p >= thr).mean()
    print(f"Routing threshold {thr:.3f}: sends {sent:.1%} of validation messages to the agent")
    json.dump({"low_threshold": thr, "target_recall": TARGET_RECALL, "share_sent_on_validation": float(sent)},
              open(ROOT / "models/threshold.json", "w"), indent=2)


if __name__ == "__main__":
    main()
