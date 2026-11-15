from scamcheck.budget import DailyBudget
from scamcheck.i18n import T, guess_language


def test_all_languages_have_same_keys():
    assert set(T["es"]) == set(T["en"]) == set(T["zh"])
    assert set(T["zh"]["stamp"]) == {"scam", "suspicious", "safe"}


def test_guess_language():
    assert guess_language("【USPS】您的包裹因地址不完整无法投递") == "zh"
    assert guess_language("Hola, ¿seguimos con el café mañana?") == "es"
    assert guess_language("Your package is on hold") == "en"


def test_budget(tmp_path):
    b = DailyBudget(tmp_path / "spend.json", 0.10)
    assert b.can_spend()
    b.add(0.06)
    assert b.can_spend()
    b.add(0.05)
    assert not b.can_spend()
    assert abs(DailyBudget(tmp_path / "spend.json", 0.10).spent_today() - 0.11) < 1e-9
