# Venture Scout — Agent Specification

## Mission
Find and organise public evidence about San Francisco startups reporting multi-million-dollar seed financings; assess investment hypotheses with a transparent, editable, evidence-weighted framework; and learn descriptively from later company outcomes.

## Non-goals
- No claim to find every private, undisclosed, or unannounced round.
- No claim of affiliation with a16z or any VC firm.
- No automatic investment recommendation, valuation, probability-of-success claim, trade, or capital allocation.
- No inference that a Form D is a seed round.
- No fabricated TAM, ARR, customer, retention, founder credentials, round terms, or cap table.

## Workflow
1. Discover candidate articles through public Google News RSS.
2. Store company data and provenance in SQLite.
3. Keep funding evidence states distinct: announced_verified, announced_unverified, sec_filing_only, and user_entered.
4. Apply nine weighted dimensions. A rating counts only with a written evidence note.
5. Show weighted score and weighted evidence coverage.
6. Require at least 60% coverage and five assessed dimensions before screening as DEEP DIVE, WATCH, or LOW PRIORITY.
7. Generate a deterministic memo, with optional LLM rewrite that is constrained to supplied evidence.
8. Record outcome labels with date and source URL. Compare groups descriptively only.

## Scorecard
- Market size & urgency: 20%
- Founder-market fit: 15%
- Traction quality: 15%
- Problem intensity: 10%
- Product wedge & 10x value: 10%
- Go-to-market repeatability: 10%
- Defensibility: 10%
- Capital efficiency: 5%
- Financing & round context: 5%

## Evidence policy
Prefer company/investor announcements and regulator filings. Record publication date, publisher, source type, URL and excerpt. Secondary coverage is a discovery lead only until confirmed. SEC Form D shows an exempt-offering notice; inspect issuer type, amount offered, amount sold, location and date of first sale separately.

## Human control
An analyst remains responsible for verifying evidence, entering ratings, recording outcomes and deciding whether to pursue a company. The system does not contact founders or investors.
