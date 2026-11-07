# Install and use Venture Scout Skill

Canonical skill: skills/venture-scout/. Native discovery copies are in .claude/skills/venture-scout/ and .agents/skills/venture-scout/.

## Claude.ai web
1. Download the standalone venture-scout-skill.zip supplied with this project.
2. Open Customize → Skills.
3. Select + → Create skill → Upload a skill.
4. Upload the ZIP and enable Venture Scout.
5. Test: "Use Venture Scout to research San Francisco AI startups with seed rounds over $2M since January 2025. Separate verified rounds from unverified leads."

Custom skills require code execution to be enabled; plan availability is controlled by Anthropic.

## Claude Code
    py skills/venture-scout/scripts/install_skill.py --target claude-code --scope user
Installs into ~/.claude/skills/venture-scout/. Add --scope project --project . for repo-only installation.

## ChatGPT desktop / Codex CLI / IDE
    py skills/venture-scout/scripts/install_skill.py --target codex --scope user
Installs into ~/.agents/skills/venture-scout/. Add --scope project --project . for repo-only installation.

OpenAI currently distinguishes standalone skills in ChatGPT desktop/Codex/IDE from plugin-distributed skills for ChatGPT web Chat and Work. This standalone ZIP is not a ChatGPT web plugin.

## Local LLM with MCP
    py -m pip install -r requirements.txt -r requirements-mcp.txt
    python -m venture_scout.mcp_server

Configure the MCP-capable host to run command python with args ["-m","venture_scout.mcp_server"] and working directory set to this repo. Set VENTURE_SCOUT_DB=data/venture_scout.db. For EDGAR, set SEC_USER_AGENT to app name plus a contact email.

## Local LLM with system prompt only
Paste prompts/venture-scout-system-prompt.md into the model's system prompt. Attach/mount the dataset and sources. Without web/MCP, no live startup discovery is available.

## Smoke tests
    py skills/venture-scout/scripts/validate_skill.py
    py -m unittest discover -s tests -v

Skills provide workflow instructions, not automatic permissions or tools. Fresh sourcing requires host web search; local DB access requires MCP or local project access.
