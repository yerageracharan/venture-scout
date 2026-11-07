# Venture Scout

**Evidence-first San Francisco seed-stage venture intelligence.** Discover publicly announced multi-million-dollar seed rounds, build a source-linked startup universe, score opportunities with an institutional-style diligence rubric, and generate investment committee-style research memos.

> Independent project. Not affiliated with Andreessen Horowitz (a16z), and does not reproduce any VC firm's proprietary investment process.

## What it does

- **Discover:** search public Google News RSS for San Francisco seed-round announcements without requiring an API key.
- **Build a company universe:** store the startup, city, sector, stage, round amount/date, investor list and source register in SQLite.
- **Verify:** distinguish primary funding announcements, secondary database entries, unverified news leads and SEC filing signals.
- **Score:** apply an explainable nine-dimension seed diligence rubric; every rating can include evidence notes and source URLs.
- **Memo:** create a deterministic research memo or optional LLM-assisted diligence memo.
- **Learn from the cohort:** compare sectors, investor frequency, round sizes and announcement years; record follow-on, acquisition and shutdown outcomes; compare early diligence signals with later outcomes descriptively.
- **Export:** download the company universe as JSON/CSV and save research memos as Markdown.

## Quick start — Windows

```powershell
py -m venv .venv
.venv\\Scripts\\activate
py -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal. The database and sample research cohort are created automatically the first time the app runs.

## Optional AI reasoning

The research, storage, scorecard and deterministic memo work without an LLM key. To enable AI-assisted memo writing, configure an OpenAI-compatible endpoint in `.env`:

```dotenv
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b-instruct
LLM_API_KEY=
```

This example uses a local Ollama-compatible server. Hosted providers can be used by supplying their compatible base URL, model and API key. The prompt instructs the model to separate facts from hypotheses, cite supplied URLs, and never invent traction or financial metrics.

## Public discovery

### News search

The Discover tab queries Google News RSS. This is a discovery feed, not a complete or authoritative funding database. Candidate company names and amounts are extracted heuristically from headlines and snippets; review the original article and a primary company/investor announcement before marking a record verified.

### SEC Form D

The SEC Form D scanner is an optional, separate evidence stream. Set a real contact email in the `SEC_USER_AGENT` value in `.env` before querying EDGAR:

```dotenv
SEC_USER_AGENT=VentureScout/0.1 (research contact: you@example.com)
```

The tool reads quarterly master indexes and inspects Form D XML for recent filings. SEC guidance says Form D is a notice of an exempt securities offering, generally filed within 15 days after the first sale. It may be filed by operating companies, funds and other issuers. The maximum offering amount and the amount sold to date are different fields; neither should automatically be labelled a seed round. Keep issuer city/state and entity type in view when reviewing. Respect SEC fair-access and privacy policies.

## Scoring methodology

| Dimension | Weight |
|---|---:|
| Market size & urgency | 20% |
| Founder-market fit | 15% |
| Traction quality | 15% |
| Problem intensity | 10% |
| Product wedge & 10x value | 10% |
| Go-to-market repeatability | 10% |
| Defensibility | 10% |
| Capital efficiency | 5% |
| Financing & round context | 5% |

Ratings use a 1–5 scale and are counted only when a written evidence note is supplied. Unknowns are left unassessed, not treated as zero. The output reports both a normalised score and evidence coverage. Below 60% weighted coverage or fewer than five assessed dimensions, the agent returns **INSUFFICIENT EVIDENCE**. Its other outputs are **DEEP DIVE**, **WATCH**, and **LOW PRIORITY**—not buy/sell recommendations.

The rubric is an original, transparent synthesis of general venture diligence practices. Public a16z writing discusses founder/market fit and distinguishing real market signals from low-quality traction claims; the project references that article for context, not as a claim of affiliation or replication.

## Starter cohort

The initial database includes seven primary-announcement-backed examples (representing $39.7M in announced seed capital) and seven additional recent candidate leads from a secondary funding roundup. The latter are deliberately marked `announced_unverified` and must be checked against individual company/investor announcements before they count as eligible deals. Examples with primary announcement sources:

| Company | Announced round | Date | Lead / notable investors |
|---|---:|---|---|
| Astor | $5.0M | 2026-04-23 | Monashees, Y Combinator |
| CodeIntegrity | $5.0M | 2026-05-27 | SYN Ventures, Antler, Boost VC |
| Katalyze AI | $10.5M | 2026-07-06 | Bonfire Ventures, Inovia Capital |
| Orthogonal | $4.3M | 2026-06-25 | Pantera Capital, Y Combinator |
| Decimal AI | $4.0M | 2026-09-15 | Khosla Ventures, Kearny Jackson |
| Sans Strings Studio | $5.5M | 2026-03-27 | Red River West, a16z speedrun |
| Catalyx Space | $5.4M | 2025-10-30 | Outlander VC |

Recent secondary-source candidate leads currently include BioStack, Watchtower Labs, Dream, Northstar Security, PreScalar, Different and Lightsprint (rounds listed from Oct 19–29, 2026). The secondary roundup says it was updated Nov 7, 2026; individual primary announcement verification remains outstanding for these leads. The universe is illustrative, not exhaustive. Company funding releases are primary sources for what the company announced; customer and traction claims still need independent diligence. Every record links its source in `data/research_seeds.json` and the app.

## Outcome learning

The app lets the analyst label later company outcomes (active, follow-on round, acquired, shut down or other) and records the date, follow-on capital and evidence URL. The Cohort Patterns tab then shows outcome counts and dimension averages by outcome where enough records exist. This is descriptive research only: the starter cohort has no outcome labels, and small selected samples cannot support return prediction. A future predictive model should use timestamped snapshots, independent test cohorts, base-rate comparisons and explicit survivorship-bias controls.

## Tests

```powershell
py -m unittest discover -s tests -v
```

## Repository layout

```text
venture-scout/
├── app.py
├── AGENT_SPEC.md
├── data/
│   ├── research_seeds.json
│   ├── starter_cohort.csv
│   └── research_snapshot.md
├── examples/
├── tests/
└── venture_scout/
    ├── cohort.py
    ├── llm.py
    ├── memo.py
    ├── models.py
    ├── scoring.py
    ├── store.py
    └── sources/
        ├── google_news.py
        └── sec_edgar.py
```

## Important limitations

- No public source can guarantee complete coverage of private, unannounced or undisclosed rounds.
- The Google News connector finds candidate stories; it does not automatically verify geography, financing stage or amounts.
- Form D includes more than venture-backed startups and is not interchangeable with a funding announcement.
- Descriptive investor/sector patterns are not predictive without longitudinal outcomes, controls and out-of-sample testing.
- Do not interpret the screening score as a valuation, probability of success or investment recommendation.

## References

- [a16z — Aligning startup metrics with stage of maturity](https://a16z.com/aligning-startup-metrics-with-stage-of-maturity-beyond-labels-for-fundraising-rounds/)
- [SEC — What is Form D?](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/what-form-d)
- [SEC — EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)


## Portable Agent Skill: Claude, ChatGPT desktop/Codex, and local LLMs

Venture Scout now includes a reusable Agent Skill following the open Agent Skills format.

- Canonical skill: [skills/venture-scout](skills/venture-scout/)
- Installation guide: [SKILL_INSTALL.md](SKILL_INSTALL.md)
- Claude Code discovery entry: [.claude/skills/venture-scout](.claude/skills/venture-scout/)
- ChatGPT desktop / Codex discovery entry: [.agents/skills/venture-scout](.agents/skills/venture-scout/)
- Local LLM system prompt: [prompts/venture-scout-system-prompt.md](prompts/venture-scout-system-prompt.md)
- Optional local MCP server: [venture_scout/mcp_server.py](venture_scout/mcp_server.py)

For Claude.ai, upload the standalone skill ZIP supplied with this project under **Customize → Skills → Create skill → Upload a skill**. For Claude Code and Codex, use the included installer script. Local models can use the system prompt or connect to the MCP server if their host supports MCP. A skill does not automatically grant web access; connect a browser/search tool for fresh funding research.
