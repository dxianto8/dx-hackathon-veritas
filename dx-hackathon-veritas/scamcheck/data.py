"""Dataset loaders."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_sms(path: Path = DATA_DIR / "SMSSpamCollection.tsv") -> pd.DataFrame:
    """UCI SMS Spam Collection. Returns columns text, label (1 = spam/scam)."""
    df = pd.read_csv(path, sep="\t", header=None, names=["raw", "text"], quoting=3, encoding="utf-8")
    df["label"] = (df.raw == "spam").astype(int)
    return df[["text", "label"]]


def load_scams2026(path: Path = DATA_DIR / "scams2026.csv") -> pd.DataFrame:
    """Our multilingual 2026 test set. Adds y (1 = scam)."""
    df = pd.read_csv(path, encoding="utf-8").fillna({"notes": ""})
    df["y"] = (df.label == "scam").astype(int)
    return df
