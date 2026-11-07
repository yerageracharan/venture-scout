# Venture Scout MCP tools

Install optional tools:
    py -m pip install -r requirements.txt -r requirements-mcp.txt
    python -m venture_scout.mcp_server

The stdio server stores records in VENTURE_SCOUT_DB (default data/venture_scout.db). On first call, an empty DB loads data/research_seeds.json; existing records are not overwritten.

Tools:
- venture_scout_list_companies — local company list with screening status.
- venture_scout_get_company — full company/source record.
- venture_scout_score_company — score, coverage and diligence gaps.
- venture_scout_search_news — Google News RSS discovery leads; not verification.
- venture_scout_save_research_lead — saves an unverified lead; article date is not round date and HQ remains unverified.
- venture_scout_write_memo — deterministic Markdown memo.
- venture_scout_analyse_cohort — verified rounds separately from unverified leads plus outcome coverage.
- venture_scout_record_outcome — sourced outcome event.
- venture_scout_scan_form_d — SEC Form D discovery only.

For a local MCP client, configure command python, args ["-m","venture_scout.mcp_server"], and working directory as this repository. Set VENTURE_SCOUT_DB and optionally SEC_USER_AGENT. Client config formats vary. A host must support local MCP; do not assume every ChatGPT, Claude or local-model surface supports it. Web discovery also requires a web/search connector.
