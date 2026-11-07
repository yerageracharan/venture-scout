from __future__ import annotations
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from html import unescape
from typing import Any

AMOUNT_RE = re.compile(r"\$\s?([\d,.]+)\s?(billion|bn|million|m|k)?\b", re.I)
STAGE_RE = re.compile(r"\b(pre[- ]?seed|seed|series\s*[abcde])\b", re.I)


def _amount_usd(text: str) -> float | None:
    match = AMOUNT_RE.search(text)
    if not match:
        return None
    try:
        value = float(match.group(1).replace(",", ""))
    except ValueError:
        return None
    unit = (match.group(2) or "").lower()
    multiplier = 1_000_000_000 if unit in {"billion", "bn"} else 1_000_000 if unit in {"million", "m"} else 1_000 if unit == "k" else 1
    return value * multiplier


def _company_from_title(title: str) -> str:
    patterns = [
        r"^(.+?)\s+(?:raises?|raised|secures?|secured|announces?|announced|closes?|closed|lands?)\b",
        r"^(.+?)\s*:\s*(?:.*seed|.*funding)",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.I)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip(" -–—:|")
    return ""


def search_google_news(query: str, days: int = 365, limit: int = 50) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("A search query is required.")
    after = (date.today() - timedelta(days=max(1, days))).isoformat()
    terms = f'({query}) ("seed round" OR "seed funding" OR "seed investment") after:{after}'
    params = urllib.parse.urlencode({"q": terms, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    url = f"https://news.google.com/rss/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "VentureScout/1.0 (research feed client)"})
    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read(5_000_000)
    root = ET.fromstring(raw)
    items: list[dict[str, Any]] = []
    for node in root.findall(".//item")[:limit]:
        title = unescape(node.findtext("title") or "")
        link = node.findtext("link") or ""
        pub = node.findtext("pubDate") or ""
        desc = re.sub(r"<[^>]+>", " ", node.findtext("description") or "")
        desc = re.sub(r"\s+", " ", unescape(desc)).strip()
        content = f"{title} {desc}"
        amount = _amount_usd(content)
        stage_match = STAGE_RE.search(content)
        items.append({
            "company_candidate": _company_from_title(title),
            "title": title,
            "url": link,
            "published_at": pub,
            "amount_usd_candidate": amount,
            "stage_candidate": stage_match.group(1).title() if stage_match else "",
            "excerpt": desc[:900],
            "status": "unverified_research_lead",
            "source_type": "news_aggregator",
        })
    return items
