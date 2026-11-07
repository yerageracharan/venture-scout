from __future__ import annotations
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP
from .models import Company, Source
from .store import Store
from .scoring import score_company, diligence_gaps
from .memo import build_memo
from .cohort import analyse_cohort, analyse_outcomes
from .sources.google_news import search_google_news
from .sources.sec_edgar import discover_form_d

mcp = FastMCP("venture-scout")

def _store() -> Store:
    store = Store(os.getenv("VENTURE_SCOUT_DB", "data/venture_scout.db"))
    seed = Path("data/research_seeds.json")
    if not store.get_all() and seed.is_file():
        for row in json.loads(seed.read_text(encoding="utf-8")):
            store.upsert(Company.from_dict(row))
    return store

def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)

@mcp.tool()
def venture_scout_list_companies(query: str = "", sector: str = "", limit: int = 100) -> str:
    """List local company records and preserve funding evidence status."""
    rows = _store().get_all()
    if query:
        q = query.casefold()
        rows = [x for x in rows if q in " ".join([x.name, x.description, x.sector, *x.investors]).casefold()]
    if sector:
        rows = [x for x in rows if x.sector.casefold() == sector.casefold()]
    out = []
    for x in rows[:max(1, min(limit, 500))]:
        s = score_company(x)
        out.append({"company_id": x.company_id, "name": x.name, "sector": x.sector, "hq_city": x.hq_city, "hq_region": x.hq_region, "stage": x.stage, "round_amount_usd": x.round_amount_usd, "round_date": x.round_date, "funding_evidence_status": x.funding_evidence_status, "score": s["score"], "coverage": s["coverage"], "verdict": s["verdict"]})
    return _json(out)

@mcp.tool()
def venture_scout_get_company(company_id: str) -> str:
    """Get a full company record and its source register."""
    c = _store().get(company_id)
    return _json(c.to_dict()) if c else _json({"error": "company not found", "company_id": company_id})

@mcp.tool()
def venture_scout_score_company(company_id: str) -> str:
    """Calculate evidence-weighted score, coverage and diligence gaps."""
    c = _store().get(company_id)
    if not c:
        return _json({"error": "company not found", "company_id": company_id})
    return _json({"company": c.name, "scorecard": score_company(c), "diligence_gaps": diligence_gaps(c)})

@mcp.tool()
def venture_scout_search_news(query: str, days: int = 365, limit: int = 40) -> str:
    """Find funding article candidates. Results are unverified discovery leads."""
    return _json(search_google_news(query, days=max(1, min(days, 1095)), limit=max(1, min(limit, 100))))

@mcp.tool()
def venture_scout_save_research_lead(name: str, description: str, source_url: str, source_title: str = "", publisher: str = "Google News RSS", sector: str = "Unknown", amount_usd_candidate: float | None = None, published_at_candidate: str = "") -> str:
    """Save an unverified lead; article date is not round date and HQ remains unverified."""
    if not name.strip() or not source_url.startswith(("https://", "http://")):
        return _json({"error": "name and valid http(s) source_url required"})
    c = Company(name=name.strip(), hq_city="Unverified", hq_region="", sector=sector or "Unknown", description=description, round_amount_usd=amount_usd_candidate, round_date="", funding_evidence_status="announced_unverified", sources=[Source(title=source_title or name, url=source_url, publisher=publisher, published_at=published_at_candidate, excerpt=description, source_type="secondary")], notes="MCP-saved unverified lead. Verify HQ, stage, amount, investor participation and primary announcement.")
    _store().upsert(c)
    return _json({"saved": True, "company_id": c.company_id, "name": c.name, "funding_evidence_status": c.funding_evidence_status})

@mcp.tool()
def venture_scout_write_memo(company_id: str) -> str:
    """Write a deterministic Markdown memo for a stored company."""
    c = _store().get(company_id)
    if not c:
        return _json({"error": "company not found", "company_id": company_id})
    path = Path("outputs") / (c.name.lower().replace(" ", "-") + "-memo.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_memo(c), encoding="utf-8")
    return _json({"written": True, "path": str(path), "company_id": c.company_id})

@mcp.tool()
def venture_scout_analyse_cohort() -> str:
    """Summarise verified rounds separately from unverified leads and outcomes."""
    cs = _store().get_all()
    return _json({"funding_cohort": analyse_cohort(cs), "outcomes": analyse_outcomes(cs)})

@mcp.tool()
def venture_scout_record_outcome(company_id: str, outcome_status: str, outcome_date: str, evidence_url: str, follow_on_round_amount_usd: float | None = None) -> str:
    """Record a later company outcome only when an evidence URL is supplied."""
    allowed = {"Active", "Follow-on round", "Acquired", "Shut down", "Other"}
    if outcome_status not in allowed:
        return _json({"error": "invalid outcome_status", "allowed": sorted(allowed)})
    if not evidence_url.startswith(("https://", "http://")):
        return _json({"error": "evidence_url required"})
    c = _store().get(company_id)
    if not c:
        return _json({"error": "company not found", "company_id": company_id})
    c.outcome_status = outcome_status
    c.outcome_date = outcome_date
    c.outcome_evidence_url = evidence_url
    c.follow_on_round_amount_usd = follow_on_round_amount_usd
    c.notes = (c.notes + chr(10) if c.notes else "") + f"Outcome evidence: {outcome_status} ({outcome_date}) — {evidence_url}"
    _store().upsert(c)
    return _json({"saved": True, "company_id": company_id, "outcome_status": outcome_status})

@mcp.tool()
def venture_scout_scan_form_d(days: int = 120, user_agent: str = "") -> str:
    """Discover SEC Form D notices; these are not automatically seed rounds."""
    agent = user_agent or os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        return _json({"error": "Set SEC_USER_AGENT to app name plus contact email"})
    end = date.today()
    start = end - timedelta(days=max(1, min(days, 365)))
    return _json(discover_form_d(start, end, agent, max_filings=100))

if __name__ == "__main__":
    mcp.run(transport="stdio")
