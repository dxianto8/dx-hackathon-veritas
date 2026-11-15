import scamcheck.pipeline as pl
from scamcheck.agent import Verdict


class FakeL1:
    def __init__(self, p): self.p = p
    def predict_proba(self, texts): return [self.p for _ in texts]


def setup(monkeypatch, p, thr=0.6):
    monkeypatch.setattr(pl, "_layer1", lambda: FakeL1(p))
    monkeypatch.setattr(pl, "_threshold", lambda: thr)


def test_low_prob_no_signals_is_safe_without_agent(monkeypatch):
    setup(monkeypatch, 0.1)
    called = []
    monkeypatch.setattr(pl, "check_with_agent", lambda *a, **k: called.append(1))
    v = pl.check_message("see you at dinner")
    assert v.verdict == "safe" and v.layer == "layer1" and not called


def test_tool_signal_routes_to_agent(monkeypatch):
    setup(monkeypatch, 0.1)
    monkeypatch.setattr(pl, "check_with_agent",
                        lambda text, p, client=None, reply_language=None: Verdict("scam", 0.9, "en", "x", layer="agent"))
    v = pl.check_message("pay toll https://ezpass-pay.top", client=object())
    assert v.layer == "agent" and v.verdict == "scam"


def test_threshold_only_route_ignores_signals(monkeypatch):
    setup(monkeypatch, 0.1)
    v = pl.check_message("pay toll https://ezpass-pay.top", route="threshold", client=object())
    assert v.layer == "layer1"


def test_no_key_falls_back_to_layer1(monkeypatch):
    setup(monkeypatch, 0.8)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    v = pl.check_message("WIN cash now")
    assert v.layer == "layer1" and v.verdict == "scam" and "isn't connected" in v.note


def test_empty_message_rejected():
    import pytest
    with pytest.raises(ValueError):
        pl.check_message("   ")


def test_budget_reached_uses_layer1(monkeypatch, tmp_path):
    from scamcheck.budget import DailyBudget
    setup(monkeypatch, 0.8)
    b = DailyBudget(tmp_path / "s.json", 0.01)
    b.add(0.02)
    called = []
    monkeypatch.setattr(pl, "check_with_agent", lambda *a, **k: called.append(1))
    v = pl.check_message("WIN cash now", client=object(), budget=b, reply_lang="es")
    assert not called and v.layer == "layer1" and "límite" in v.note


def test_reply_language_passed_to_agent(monkeypatch):
    setup(monkeypatch, 0.9)
    seen = {}
    def fake(text, p, client=None, reply_language=None):
        seen["lang"] = reply_language
        return Verdict("scam", 0.9, "en", "x", layer="agent", cost_usd=0.04)
    monkeypatch.setattr(pl, "check_with_agent", fake)
    pl.check_message("WIN cash now", client=object(), reply_lang="zh")
    assert seen["lang"] == "Simplified Chinese"


def test_safe_message_translated_when_language_differs(monkeypatch):
    setup(monkeypatch, 0.05)
    monkeypatch.setattr(pl, "translate", lambda text, lang, client=None: ("见你", 0.002))
    v = pl.check_message("see you at dinner", client=object(), reply_lang="zh")
    assert v.verdict == "safe" and v.translation == "见你" and v.explanation.startswith("没有")


def test_safe_message_same_language_not_translated(monkeypatch):
    setup(monkeypatch, 0.05)
    monkeypatch.setattr(pl, "translate", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call")))
    v = pl.check_message("see you at dinner", client=object(), reply_lang="en")
    assert v.translation == ""
