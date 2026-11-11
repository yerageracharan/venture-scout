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

## Change ownership and proof

- Keep one authoritative owner for each domain rule and each persisted state. UI, CLI, MCP, and provider adapters translate inputs and outputs; they must not reimplement business policy or become competing sources of truth.
- Before changing a contract, trace the input through its owner to every consumer. Update callers, schemas, examples, docs, and regression tests together. Remove superseded paths unless a documented public-compatibility requirement keeps them.
- Keep optional external model/provider integrations behind adapters. Use injected or mocked adapters for deterministic unit tests; label live network/provider checks separately and never describe a mock as live verification.
- Validate untrusted user, model, file, and network data at the boundary. Preserve the product's evidence/provenance rules and reject malformed inputs rather than silently inventing defaults.
- Verify the supported user entry point and at least one relevant failure path. Report exact commands and results; CI on a different commit SHA is not proof for the current change.
- Keep the root README as the user entry point, `docs/README.md` as the documentation map, and focused guides as the owners of detailed contracts. Update links when files move. Do not hand-edit generated output when a source or generator owns it.


## Repository automation rules

- Treat files under `.github/workflows/` as production code. When changing a workflow, inspect the triggered run for the exact commit SHA; a prior green run is not proof for a newer commit.
- Pin third-party GitHub Actions to full 40-character commit SHAs and keep the upstream release tag in a trailing comment. Do not replace a pinned SHA with a floating major-version tag.
- Use the least-privilege `permissions` block. Default to read-only; grant write access only to the specific job that must publish or commit generated output.
- Give every job a finite `timeout-minutes`. Add a clear `concurrency` group for expensive or supersedable work; cancel stale pull-request runs, but do not cancel workflows whose purpose is to publish a completed artifact or evidence.
- Keep workflow logs and uploaded artifacts free of secrets and personal data. Set retention to the shortest period that still serves the evaluation or debugging purpose.
- Rely on the existing Dependabot configuration for action updates, then review release notes and run the affected workflow before considering the update complete.
