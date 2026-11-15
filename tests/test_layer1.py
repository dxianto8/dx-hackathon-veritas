import numpy as np

from scamcheck.layer1 import Layer1, choose_low_threshold, train_tfidf_baseline

TEXTS = ["WIN a free cash prize, claim now at this link", "URGENT you have won 1000 dollars call now",
         "Free entry to win a new phone, text WIN", "Congratulations you won a voucher, claim today",
         "see you at dinner", "can you pick me up at 6", "running late, save me a seat", "thanks for the help today"]
LABELS = [1, 1, 1, 1, 0, 0, 0, 0]


def test_layer1_ranks_spam_higher():
    m = Layer1().fit(TEXTS, LABELS)
    p = m.predict_proba(["WIN cash prize claim now", "see you at dinner tonight"])
    assert p[0] > p[1]


def test_layer1_save_load(tmp_path):
    m = Layer1().fit(TEXTS, LABELS)
    m.save(tmp_path / "m.joblib")
    m2 = Layer1.load(tmp_path / "m.joblib")
    assert np.allclose(m.predict_proba(TEXTS), m2.predict_proba(TEXTS))


def test_tfidf_baseline():
    pipe = train_tfidf_baseline(TEXTS, LABELS)
    assert pipe.predict_proba(["win free prize now"])[0, 1] > 0.5


def test_choose_low_threshold():
    probs = np.array([0.05, 0.1, 0.3, 0.6, 0.9, 0.95])
    labels = np.array([0, 0, 1, 0, 1, 1])
    t = choose_low_threshold(probs, labels, target_recall=1.0)
    assert t <= 0.3
    assert ((probs >= t) & (labels == 1)).sum() == 3
