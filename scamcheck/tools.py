"""Investigation tools the Claude agent can call. Pure Python, no network."""
import ipaddress
import json
import re
from functools import lru_cache

from .data import DATA_DIR

# Domain-like tokens, with or without a scheme. ASCII only, so Chinese text
# around a link is not swallowed.
URL_RE = re.compile(
    r"(?:https?://)?(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(?::\d+)?(?:/[\x21-\x7e]*)?"
    r"|https?://\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?(?:/[\x21-\x7e]*)?",
    re.IGNORECASE,
)
COMMON_TLDS = {"com", "org", "net", "gov", "edu", "us", "uk", "mx", "cn", "io", "co", "app", "me", "ly", "at", "gd", "gl"}


@lru_cache
def _brand_data():
    return json.loads((DATA_DIR / "brand_domains.json").read_text(encoding="utf-8"))


@lru_cache
def _pattern_data():
    return json.loads((DATA_DIR / "known_patterns.json").read_text(encoding="utf-8"))


def _edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _host(url: str) -> str:
    host = re.sub(r"^https?://", "", url, flags=re.I).split("/")[0].split(":")[0].lower()
    return host[4:] if host.startswith("www.") else host


def _is_official(host: str, official: list[str]) -> bool:
    return any(host == d or host.endswith("." + d) for d in official)


def _link_flags(host: str) -> list[str]:
    data = _brand_data()
    try:
        ipaddress.ip_address(host)
        return ["ip_address"]
    except ValueError:
        pass
    flags = []
    if "xn--" in host:
        flags.append("punycode")
    if host in data["shorteners"]:
        flags.append("shortener")
    tld = host.rsplit(".", 1)[-1]
    if tld in data["risky_tlds"]:
        flags.append(f"risky_tld:.{tld}")
    for brand, official in data["brands"].items():
        if _is_official(host, official):
            return [f"official_domain:{brand}"]
    labels = host.rsplit(".", 1)[0]  # everything except the TLD
    parts = re.split(r"[.\-]", labels)
    squashed = labels.replace("-", "").replace(".", "")
    for brand in data["brands"]:
        if brand in squashed and len(brand) >= 3:
            flags.append(f"brand_in_unofficial_domain:{brand}")
            continue
        if len(brand) >= 4 and any(0 < _edit_distance(p, brand) <= (1 if len(brand) < 6 else 2) for p in parts if len(p) >= 3):
            flags.append(f"lookalike:{brand}")
    return flags


def analyze_links_impl(text: str) -> dict:
    links = []
    for m in URL_RE.finditer(text):
        url = m.group(0).rstrip(".,;:!?)")
        host = _host(url)
        tld = host.rsplit(".", 1)[-1]
        if not re.match(r"^\d", host) and not url.lower().startswith("http") and tld not in COMMON_TLDS and tld not in _brand_data()["risky_tlds"]:
            continue  # e.g. "Dr.Smith" — not a link
        links.append({"url": url, "domain": host, "flags": _link_flags(host)})
    if not links:
        summary = "No links found."
    else:
        risky = [l for l in links if any(not f.startswith("official_domain") for f in l["flags"])]
        summary = f"{len(links)} link(s); {len(risky)} with warning signs."
    return {"links": links, "summary": summary}


def match_known_patterns_impl(text: str) -> dict:
    t = text.lower()
    data = _pattern_data()
    matches = []
    for p in data["patterns"]:
        hits = [k for k in p["keywords"] if k in t]
        if hits:
            matches.append({"pattern_id": p["id"], "name": p["name"], "score": len(hits),
                            "matched_keywords": hits, "source_url": p["source_url"]})
    matches.sort(key=lambda m: -m["score"])
    urgency = [k for k in data["urgency_keywords"] if k in t]
    return {"matches": matches, "urgency_words": urgency}
