from scamcheck.data import load_sms, load_scams2026


def test_load_sms():
    df = load_sms()
    assert len(df) == 5574
    assert set(df.label.unique()) == {0, 1}
    assert 0.12 < df.label.mean() < 0.15


def test_load_scams2026():
    df = load_scams2026()
    assert df.source_url.str.len().min() > 0
    assert set(df.language.unique()) <= {"en", "es", "zh"}
    counts = df.groupby(["language", "label"]).size()
    assert counts.min() >= 15
