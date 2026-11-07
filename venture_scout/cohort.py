from __future__ import annotations
from collections import Counter
from statistics import median
from .models import Company, DIMENSIONS


def analyse_cohort(companies: list[Company]) -> dict:
    funded = [c for c in companies if c.round_amount_usd and c.round_amount_usd > 0 and c.funding_evidence_status == "announced_verified"]
    unverified = [c for c in companies if c.round_amount_usd and c.round_amount_usd > 0 and c.funding_evidence_status != "announced_verified"]
    sectors = Counter(c.sector for c in funded if c.sector and c.sector != "Unknown")
    investors = Counter(i for c in funded for i in c.investors)
    amounts = [c.round_amount_usd for c in funded]
    years = Counter((c.round_date or "")[:4] for c in funded if c.round_date)
    return {
        "company_count": len(companies),
        "funded_records": len(funded),
        "unverified_funding_leads": len(unverified),
        "median_round_usd": median(amounts) if amounts else None,
        "total_announced_usd": sum(amounts) if amounts else 0,
        "sector_counts": sectors.most_common(),
        "investor_counts": investors.most_common(15),
        "year_counts": years.most_common(),
        "caveat": "Statistics below use only records marked announced_verified with a source-backed funding announcement. Unverified funding leads are counted separately and excluded from round-size, sector and investor statistics. This is not the full San Francisco startup universe; investor frequency does not establish causality or investment quality.",
    }


def analyse_outcomes(companies: list[Company]) -> dict:
    """Descriptive early-signal/outcome comparison; intentionally not a predictive model."""
    labelled = [c for c in companies if c.outcome_status and c.outcome_status != "Unknown"]
    outcomes: dict[str, int] = Counter(c.outcome_status for c in labelled)
    dimension_avgs = {}
    for key, spec in DIMENSIONS.items():
        groups = {}
        for label in sorted(outcomes):
            values = [c.dimensions[key].rating for c in labelled if c.outcome_status == label and key in c.dimensions and c.dimensions[key].rating is not None]
            if values:
                groups[label] = round(sum(values) / len(values), 2)
        if groups:
            dimension_avgs[spec["label"]] = groups
    return {
        "labelled_companies": len(labelled),
        "outcome_counts": sorted(outcomes.items()),
        "dimension_averages_by_outcome": dimension_avgs,
        "warning": "Exploratory only. Small, selected and survivorship-biased samples cannot establish predictive power or causality. Preserve time-stamped point-in-time data and validate on later cohorts before using a model to rank investments.",
    }
