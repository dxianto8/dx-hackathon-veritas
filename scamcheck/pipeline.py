"""Routes a message through Layer 1 and, when needed, the Claude agent."""
import json
import os
from functools import lru_cache
from pathlib import Path

from .agent import Verdict, check_with_agent
from .layer1 import Layer1
from .tools import analyze_links_impl, match_known_patterns_impl

MODELS = Path(__file__).resolve().parent.parent / "models"


@lru_cache
def _layer1():
    return Layer1.load(MODELS / "layer1.joblib")


@lru_cache
def _threshold() -> float:
    return json.load(open(MODELS / "threshold.json"))["low_threshold"]


def tool_signals(text: str) -> list[str]:
    """Cheap rule-based warning signs: risky link flags and known-pattern matches."""
    flags = [f for l in analyze_links_impl(text)["links"] for f in l["flags"] if not f.startswith("official_domain")]
    patterns = [m["pattern_id"] for m in match_known_patterns_impl(text)["matches"]]
    return flags + [f"pattern:{p}" for p in patterns]


def should_route(prob: float, signals: list[str], route: str = "signals") -> bool:
    if route == "threshold":
        return prob >= _threshold()
    return prob >= _threshold() or bool(signals)


def check_message(text: str, use_agent: bool = True, client=None, route: str = "signals") -> Verdict:
    """route='signals' (default): send to the agent if Layer 1 is unsure/flags it OR the tools see warning
    signs. route='threshold': Layer 1 probability only (threshold chosen on English validation data)."""
    if not text or not text.strip():
        raise ValueError("Please paste a text message to check.")
    p = float(_layer1().predict_proba([text])[0])
    signals = tool_signals(text)
    if not should_route(p, signals, route):
        return Verdict("safe", round(1 - p, 2), "", "No warning signs found. This looks like a normal message.",
                       layer="layer1", layer1_prob=p)
    if use_agent and (client is not None or os.environ.get("ANTHROPIC_API_KEY")):
        return check_with_agent(text, p, client=client)
    verdict = "scam" if p >= 0.5 else "suspicious"
    return Verdict(verdict, round(max(p, 1 - p), 2), "", "Layer 1 thinks this may be a scam. Don't tap links; "
                   "contact the company through its official website.", red_flags=signals, layer="layer1",
                   layer1_prob=p, note="Claude agent not used (no ANTHROPIC_API_KEY set).")
