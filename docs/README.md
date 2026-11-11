# Documentation map

The [project README](../README.md) is the canonical product and user guide. It covers the research workflow, source hierarchy, evidence-backed scoring, dashboard, reusable Agent Skill, MCP tools, privacy, and responsible-use limitations.

## Research methodology and visual references

- [Diligence workflow](visuals/01-diligence-pipeline.svg) — thesis, sources, claims, and diligence.
- [Evidence ladder](visuals/02-evidence-ladder.svg) — distinguish primary records, company claims, independent evidence, and hypotheses.
- [Research workflow illustration](images/research-workflow.svg)
- [Evidence ladder illustration](images/evidence-ladder.svg)
- [Project hero](images/venture-scout-hero.svg)

## Reusable research assets

| Area | Source | Purpose |
|---|---|---|
| Agent behavior contract | [AGENT_SPEC.md](../AGENT_SPEC.md) | Product scope and evidence rules |
| Research prompt | [System prompt](../prompts/venture-scout-system-prompt.md) | Optional model-assisted memo drafting |
| Skill entry point | [Venture Scout skill](../skills/venture-scout/SKILL.md) | Reusable research workflow |
| Investment framework | [Framework reference](../skills/venture-scout/references/investment-framework.md) | Evaluation dimensions and questions |
| Memo format | [Memo template](../skills/venture-scout/references/investment-memo-template.md) | Standardised diligence output |
| Source policy | [Source policy](../skills/venture-scout/references/source-policy.md) | Evidence quality and attribution |
| MCP tool contract | [MCP tools](../skills/venture-scout/references/mcp-tools.md) | Available local assistant tools |
| Example output | [Diligence memo](../examples/astor-initial-diligence-memo.md) | Example of an evidence-backed write-up |

## Code ownership map

- `venture_scout/sources/` — external source adapters, including SEC and news discovery.
- `venture_scout/scoring.py` — deterministic weighted evidence scoring.
- `venture_scout/cohort.py` and `venture_scout/store.py` — research cohort and local persistence.
- `venture_scout/memo.py` — structured memo generation.
- `venture_scout/llm.py` — optional model integration.
- `venture_scout/mcp_server.py` — local MCP interface.
- `app.py` — research dashboard.
- `tests/` — scoring, sources, and cohort persistence regression tests.

## Governance and validation

- [Contribution workflow](../CONTRIBUTING.md)
- [AI coding-agent instructions](../AGENTS.md)
- [Security policy](../SECURITY.md)
- [Automated tests](../tests/)
- [Examples](../examples/)

A rating without supporting evidence is not a verified investment fact. Scores are prioritisation aids, not investment recommendations or forecasts of returns.
