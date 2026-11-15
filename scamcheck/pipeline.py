"""Routes a message through Layer 1 and, when needed, the Claude agent."""
import json
import os
from functools import lru_cache
from pathlib import Path

from .agent import Verdict, check_with_agent, translate
from .budget import DailyBudget
from .i18n import LANG_NAMES, T, guess_language
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


def check_message(text: str, use_agent: bool = True, client=None, route: str = "signals",
                  reply_lang: str | None = None, budget: DailyBudget | None = None) -> Verdict:
    """route='signals' (default): send to the agent if Layer 1 is unsure/flags it OR the tools see warning
    signs. route='threshold': Layer 1 probability only (threshold chosen on English validation data).
    reply_lang: 'en' | 'es' | 'zh' — language for the explanation and translation; None = message's language.
    budget: optional daily spending cap for Claude calls."""
    if not text or not text.strip():
        raise ValueError(T[reply_lang or "en"]["empty"])
    ui = T[reply_lang or "en"]
    p = float(_layer1().predict_proba([text])[0])
    signals = tool_signals(text)
    api_ok = use_agent and (client is not None or bool(os.environ.get("ANTHROPIC_API_KEY")))
    within_budget = budget is None or budget.can_spend()
    target = LANG_NAMES[reply_lang] if reply_lang else None

    if not should_route(p, signals, route):
        v = Verdict("safe", round(1 - p, 2), "", ui["safe_expl"], layer="layer1", layer1_prob=p)
        if target and api_ok and within_budget and guess_language(text) != reply_lang:
            v.translation, v.cost_usd = translate(text, target, client=client)
            if budget:
                budget.add(v.cost_usd)
        return v

    if api_ok and within_budget:
        v = check_with_agent(text, p, client=client, reply_language=target)
        if v.note == "agent gave no verdict":
            v.explanation = ui["inconclusive"]
        if budget:
            budget.add(v.cost_usd)
        return v

    note = ui["cap_note"] if (api_ok and not within_budget) else ui["no_key_note"]
    verdict = "scam" if p >= 0.5 else "suspicious"
    return Verdict(verdict, round(max(p, 1 - p), 2), "", ui["risky_expl"], red_flags=signals, layer="layer1",
                   layer1_prob=p, note=note)
