# Contributing

Thanks for improving Venture Scout. The product is an evidence-first research and diligence workspace. The quality bar is traceability and honest uncertainty—not a confident-looking score.

## Before changing code

- Search existing issues and commits for related work.
- Open an issue before adding diligence dimensions, changing scoring, altering source ingestion, or changing data schemas. Include the user problem, thesis, alternatives, and validation plan.
- For defects, provide synthetic company data and source examples, exact commands, expected behavior, and redacted logs.
- Keep scoring, source ingestion, UI, MCP, and skill-package changes focused.

## Development setup

Python 3.11 or newer.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Validation

```bash
python -m pytest -q
python skills/venture-scout/scripts/validate_skill.py
python -m py_compile venture_scout/mcp_server.py
```

For scoring changes, add tests for missing evidence, incomplete coverage, malformed ratings, and score boundaries. For source-ingestion changes, include date-window, pagination, rate-limit, and malformed-response tests using mocked network responses.

## Engineering expectations

- Preserve source URLs, dates, and claim provenance in data and reports.
- Clearly label company-provided claims versus independent evidence.
- Keep diligence gaps visible; do not infer missing traction, customers, funding, or founder facts.
- Make score coverage and method limitations explicit.
- Do not state that the model or rubric predicts returns or is investment advice.
- Update the methodology documentation when dimensions, weights, or thresholds change.

## Pull requests

Use the repository PR template. Include the problem, user impact, scoring/source implications, exact tests/results, and remaining evidence gaps. Link a related issue for non-trivial work.

## Security

Follow [SECURITY.md](SECURITY.md) for private vulnerability disclosure. Never commit API keys, private pitch decks, confidential founder data, or unredacted source exports.
