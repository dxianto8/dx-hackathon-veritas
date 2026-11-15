"""Layer 1: multilingual sentence embeddings + logistic regression."""
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache
def _encoder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL)


def embed(texts) -> np.ndarray:
    return _encoder().encode(list(texts), batch_size=64, normalize_embeddings=True, show_progress_bar=False)


class Layer1:
    def __init__(self, clf: LogisticRegression | None = None):
        self.clf = clf or LogisticRegression(class_weight="balanced", max_iter=2000, C=1.0)

    def fit(self, texts, labels) -> "Layer1":
        self.clf.fit(embed(texts), np.asarray(labels))
        return self

    def predict_proba(self, texts) -> np.ndarray:
        """Probability that each message is a scam."""
        return self.clf.predict_proba(embed(texts))[:, 1]

    def save(self, path: Path) -> None:
        joblib.dump(self.clf, path)

    @classmethod
    def load(cls, path: Path) -> "Layer1":
        return cls(joblib.load(path))


def train_tfidf_baseline(texts, labels):
    """The brief's suggested model: TF-IDF words + logistic regression."""
    pipe = make_pipeline(TfidfVectorizer(lowercase=True), LogisticRegression(class_weight="balanced", max_iter=2000))
    return pipe.fit(list(texts), list(labels))


def choose_low_threshold(probs, labels, target_recall: float = 0.97) -> float:
    """Highest threshold that still sends >= target_recall of scams onward (prob >= threshold)."""
    probs, labels = np.asarray(probs), np.asarray(labels)
    scam_probs = np.sort(probs[labels == 1])
    k = int(np.floor((1 - target_recall) * len(scam_probs) + 1e-9))
    return float(scam_probs[k])
