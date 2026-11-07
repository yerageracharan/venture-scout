from __future__ import annotations
from typing import Any
from .models import Company, DIMENSIONS


def score_company(company: Company) -> dict[str, Any]:
    weighted = 0.0
    assessed_weight = 0
    details = []
    for key, spec in DIMENSIONS.items():
        ev = company.dimensions.get(key)
        rating = ev.rating if ev else None
        valid = rating is not None and 1 <= int(rating) <= 5 and bool(ev and ev.evidence.strip())
        if valid:
            weighted += (int(rating) / 5.0) * spec["weight"]
            assessed_weight += spec["weight"]
        details.append({
            "key": key,
            "label": spec["label"],
            "weight": spec["weight"],
            "rating": int(rating) if valid else None,
            "weighted_points": round((int(rating) / 5.0) * spec["weight"], 2) if valid else None,
            "evidence": ev.evidence if ev else "",
            "source_urls": ev.source_urls if ev else [],
        })
    score = round(weighted / assessed_weight * 100, 1) if assessed_weight else None
    coverage = round(assessed_weight, 1)
    if coverage < 60 or sum(1 for d in details if d["rating"] is not None) < 5:
        verdict = "INSUFFICIENT EVIDENCE"
        action = "Collect primary evidence before forming an investment view."
    elif score >= 80:
        verdict = "DEEP DIVE"
        action = "Prioritise partner-level diligence; pressure-test the strongest claims."
    elif score >= 65:
        verdict = "WATCH"
        action = "Track milestone progress and close the highest-impact evidence gaps."
    else:
        verdict = "LOW PRIORITY"
        action = "Document the disconfirming evidence; revisit only if facts materially change."
    return {
        "score": score,
        "coverage": coverage,
        "dimensions_assessed": sum(1 for d in details if d["rating"] is not None),
        "verdict": verdict,
        "recommended_action": action,
        "dimensions": details,
        "method_note": "Weighted analyst rubric. The score is a prioritisation aid, not an investment recommendation or a forecast of returns.",
    }


def diligence_gaps(company: Company) -> list[str]:
    gaps: list[str] = []
    critical_fields = {
        "Founder-market fit": company.founder_notes,
        "Customer / usage evidence": company.customer_evidence,
        "Go-to-market motion": company.go_to_market,
        "Unit economics / capital intensity": company.economics,
        "Risks and failure modes": company.risks,
    }
    gaps.extend([f"Missing: {label}" for label, value in critical_fields.items() if not value.strip()])
    for key, spec in DIMENSIONS.items():
        ev = company.dimensions.get(key)
        if not ev or ev.rating is None:
            gaps.append(f"Unassessed: {spec['label']}")
        elif not ev.evidence.strip():
            gaps.append(f"Evidence missing for: {spec['label']}")
    if not company.sources:
        gaps.append("No source URLs attached; verify funding, location, product and traction claims.")
    return gaps
