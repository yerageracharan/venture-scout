from __future__ import annotations
from .models import Company
from .scoring import score_company, diligence_gaps


def build_memo(company: Company) -> str:
    result = score_company(company)
    amount = f"${company.round_amount_usd:,.0f}" if company.round_amount_usd else "Not publicly confirmed"
    source_lines = [f"- [{s.title or s.publisher or s.url}]({s.url}) — {s.source_type}; {s.published_at}" for s in company.sources]
    if not source_lines:
        source_lines = ["- No sources attached. Treat all company and funding claims as unverified."]
    score_lines = []
    for item in result["dimensions"]:
        rating = f"{item['rating']}/5" if item["rating"] is not None else "Not assessed"
        score_lines.append(f"- **{item['label']}** ({item['weight']}%): {rating}. {item['evidence'] or 'No evidence recorded.'}")
    gaps = diligence_gaps(company)
    return f"""# Investment research memo: {company.name}

> **Screening status:** {result['verdict']}  
> **Weighted score:** {result['score'] if result['score'] is not None else 'Not scored'} / 100  
> **Evidence coverage:** {result['coverage']}%  
> **Funding status:** {company.funding_evidence_status}

## 1. Company snapshot

- **Headquarters:** {company.hq_city}, {company.hq_region}
- **Sector:** {company.sector}
- **Stage:** {company.stage}
- **Announced round:** {amount}
- **Round date:** {company.round_date or 'Not confirmed'}
- **Investors:** {', '.join(company.investors) if company.investors else 'Not confirmed'}

{company.description or 'No company description recorded.'}

## 2. Investment hypothesis

**Potential wedge:** {company.description or 'Not yet established from available evidence.'}

This is a hypothesis to test, not a conclusion. Identify the initial buyer, the urgent workflow, the budget owner, and the trigger that makes the product a must-have now.

## 3. Scorecard

{chr(10).join(score_lines)}

**Suggested next action:** {result['recommended_action']}

## 4. Diligence gaps

{chr(10).join('- ' + g for g in gaps) if gaps else '- No obvious gaps recorded; continue independent verification.'}

## 5. Risks and disconfirming evidence

{company.risks or 'Not yet documented. Explicitly test incumbent response, adoption friction, data access, gross margin, regulatory exposure, and whether the product is a feature rather than a company.'}

## 6. Source register

{chr(10).join(source_lines)}

## 7. IC view

**Preliminary disposition:** {result['verdict']}. Do not make an investment decision from this memo alone. Require primary-source verification, customer references, cohort/retention data, bottom-up market sizing, founder references, cap table, round terms, and scenario-based ownership/dilution analysis.

---
*Venture Scout is an independent research tool. Its rubric is an original public-information diligence framework inspired by general institutional venture practices; it is not a16z software, advice, or proprietary methodology.*
"""
