from scamcheck.tools import analyze_links_impl, match_known_patterns_impl


def flags_for(text):
    return [f for link in analyze_links_impl(text)["links"] for f in link["flags"]]


def test_lookalike():
    assert "lookalike:paypal" in flags_for("secure now: paypa1-support.com/secure")


def test_brand_in_unofficial_domain():
    assert "brand_in_unofficial_domain:usps" in flags_for("https://usps-redelivery.top/us")


def test_shortener():
    assert "shortener" in flags_for("pay https://bit.ly/abc")


def test_ip_address():
    assert "ip_address" in flags_for("login http://45.137.21.9/boa/login")


def test_punycode():
    assert "punycode" in flags_for("https://xn--usp-1na.com/track")


def test_risky_tld():
    assert "risky_tld:.top" in flags_for("go to example-pay.top now")


def test_official_domain_not_flagged():
    res = analyze_links_impl("Track: https://www.ups.com/track?tracknum=1Z9")
    assert res["links"][0]["flags"] == ["official_domain:ups"]


def test_no_links():
    res = analyze_links_impl("see you at dinner, Dr. Smith said hi")
    assert res["links"] == []


def test_chinese_text_link():
    assert "shortener" in flags_for("请点击：https://bit.ly/3guanshui")


def test_patterns_toll():
    ids = [m["pattern_id"] for m in match_known_patterns_impl("Unpaid toll balance, pay now")["matches"]]
    assert ids[0] == "toll_fee"


def test_patterns_consulate_zh():
    ids = [m["pattern_id"] for m in match_known_patterns_impl("【中国驻芝加哥总领事馆】您有一份重要文件待领取")["matches"]]
    assert "authority_impersonation" in ids


def test_patterns_none():
    assert match_known_patterns_impl("happy birthday!")["matches"] == []
