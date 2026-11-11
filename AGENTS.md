# Agent Instructions

These instructions apply across Venture Scout.

## Product invariants

- Every material company claim must be tied to a source URL and, where available, the source date.
- Separate company statements, independently verified facts, analyst interpretation, and unknowns.
- Never turn missing evidence into a positive signal or a confident score.
- Weighted scores are prioritization aids, not investment recommendations, valuations, or forecasts of returns.
- Keep diligence gaps visible and make scoring coverage explicit; incomplete evidence must not look like a complete assessment.

## Repository map

- `venture_scout/`: data models, source ingestion, scoring, storage, and report logic.
- `app.py`: Streamlit workspace.
- `prompts/`: prompt assets.
- `skills/`: installable agent skill and its validation script.
- `examples/` and `data/`: sample and local research data; never add confidential real-world material.
- `tests/`: scoring, source, and workflow regression tests.

## Working rules

- Treat each source as evidence with provenance, not as ground truth by default.
- Preserve date and source information when extracting or summarizing claims.
- Do not invent revenue, ARR, customer counts, funding, valuations, founder background, or market metrics.
- A missing dimension must remain missing; do not silently impute a favorable score.
- Keep scoring calculations deterministic and document the exact weighting/coverage semantics.
- If external research is involved, mock network access in tests and exercise rate-limit/error handling.
- Do not commit private decks, customer lists, personal contact details, or credentials.

## Validation

```bash
python -m pytest -q
python skills/venture-scout/scripts/validate_skill.py
python -m py_compile venture_scout/mcp_server.py
```
