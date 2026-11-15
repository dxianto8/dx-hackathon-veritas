from types import SimpleNamespace

from scamcheck.agent import check_with_agent


def _usage():
    return SimpleNamespace(input_tokens=1000, output_tokens=200,
                           cache_creation_input_tokens=0, cache_read_input_tokens=0)


class FakeMessages:
    def __init__(self, submit_args=None, stop_reason="end_turn"):
        self.submit_args, self.stop_reason, self.calls = submit_args, stop_reason, []

    def tool_runner(self, **kwargs):
        self.calls.append(kwargs)
        tools = {t.name: t for t in kwargs["tools"]}
        assert {"analyze_links", "match_known_patterns", "submit_verdict"} <= set(tools)
        if self.submit_args:
            tools["submit_verdict"].call(self.submit_args)
        return [SimpleNamespace(usage=_usage(), stop_reason=self.stop_reason, content=[])]


def fake_client(**kw):
    msgs = FakeMessages(**kw)
    return SimpleNamespace(beta=SimpleNamespace(messages=msgs)), msgs


def test_agent_returns_submitted_verdict():
    client, msgs = fake_client(submit_args={"verdict": "scam", "confidence": 0.92, "language": "es",
                                            "explanation": "Pide pagar un peaje por un enlace falso.",
                                            "red_flags": ["lookalike link", "urgency"]})
    v = check_with_agent("E-ZPass: pague ahora https://ezpass-pagos.top", 0.7, client=client)
    assert v.verdict == "scam" and v.language == "es" and v.layer == "agent"
    assert v.red_flags == ["lookalike link", "urgency"]
    assert abs(v.cost_usd - (1000 * 4 + 200 * 20) / 1e6) < 1e-9
    assert msgs.calls[0]["model"] == "claude-opus-5-5"


def test_agent_without_submit_is_inconclusive():
    client, _ = fake_client()
    v = check_with_agent("hello", 0.7, client=client)
    assert v.verdict == "suspicious"
    assert "inconclusive" in v.explanation.lower()


def test_agent_refusal_is_inconclusive():
    client, _ = fake_client(stop_reason="refusal")
    v = check_with_agent("hello", 0.7, client=client)
    assert v.verdict == "suspicious"
