from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any
import hashlib


@dataclass
class Source:
    title: str
    url: str
    publisher: str = ""
    published_at: str = ""
    excerpt: str = ""
    source_type: str = "announcement"  # announcement | filing | company_site | secondary | other


@dataclass
class DimensionEvidence:
    rating: int | None = None  # 1..5; None means not assessed
    evidence: str = ""
    source_urls: list[str] = field(default_factory=list)


@dataclass
class Company:
    name: str
    hq_city: str = "San Francisco"
    hq_region: str = "CA"
    sector: str = "Unknown"
    stage: str = "Seed"
    round_amount_usd: float | None = None
    round_date: str = ""
    description: str = ""
    investors: list[str] = field(default_factory=list)
    founder_notes: str = ""
    customer_evidence: str = ""
    go_to_market: str = ""
    economics: str = ""
    risks: str = ""
    funding_evidence_status: str = "announced_unverified"  # announced_verified | announced_unverified | sec_filing_only | user_entered
    sources: list[Source] = field(default_factory=list)
    dimensions: dict[str, DimensionEvidence] = field(default_factory=dict)
    company_id: str = ""
    notes: str = ""
    outcome_status: str = "Unknown"  # Unknown | Active | Follow-on round | Acquired | Shut down | Other
    outcome_date: str = ""
    follow_on_round_amount_usd: float | None = None
    outcome_evidence_url: str = ""

    def __post_init__(self) -> None:
        if not self.company_id:
            key = f"{self.name.strip().lower()}|{self.hq_city.strip().lower()}|{self.hq_region.strip().lower()}"
            self.company_id = hashlib.sha1(key.encode("utf-8")).hexdigest()[:14]
        normalised: dict[str, DimensionEvidence] = {}
        for key, value in self.dimensions.items():
            if isinstance(value, DimensionEvidence):
                normalised[key] = value
            elif isinstance(value, dict):
                normalised[key] = DimensionEvidence(**value)
        self.dimensions = normalised
        self.sources = [s if isinstance(s, Source) else Source(**s) for s in self.sources]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Company":
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DIMENSIONS: dict[str, dict[str, Any]] = {
    "market": {"label": "Market size & urgency", "weight": 20, "question": "Is the market large, growing, urgent, and economically important?"},
    "founder_edge": {"label": "Founder-market fit", "weight": 15, "question": "Does the team have a non-obvious insight, relevant experience, or execution edge?"},
    "problem": {"label": "Problem intensity", "weight": 10, "question": "Is the pain frequent, expensive, unavoidable, and owned by a clear buyer?"},
    "product": {"label": "Product wedge & 10x value", "weight": 10, "question": "Is the first product meaningfully better than the status quo?"},
    "traction": {"label": "Traction quality", "weight": 15, "question": "Is there evidence of real usage, retention, paid deployment, or repeat demand?"},
    "distribution": {"label": "Go-to-market repeatability", "weight": 10, "question": "Is there a credible path to repeatable, scalable customer acquisition?"},
    "moat": {"label": "Defensibility", "weight": 10, "question": "Can an advantage compound through data, workflow, network effects, IP, regulation, or cost?"},
    "capital_efficiency": {"label": "Capital efficiency", "weight": 5, "question": "Can the company reach meaningful milestones with reasonable capital intensity?"},
    "financing_context": {"label": "Financing & round context", "weight": 5, "question": "Is the round size, timing, investor fit, and use of proceeds coherent with the plan?"},
}
