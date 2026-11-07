#!/usr/bin/env python3
"""Validate the minimal Agent Skills manifest and references."""
from pathlib import Path
import re
import sys

def main():
    root = Path(__file__).resolve().parents[1]
    manifest = root / "SKILL.md"
    if not manifest.is_file():
        print("FAIL: SKILL.md missing")
        return 1
    text = manifest.read_text(encoding="utf-8")
    if not text.startswith("---" + chr(10)):
        print("FAIL: YAML frontmatter missing")
        return 1
    parts = text.split("---", 2)
    if len(parts) < 3:
        print("FAIL: malformed frontmatter")
        return 1
    front = parts[1]
    name = re.search(r"(?m)^name:\s*([a-z0-9][a-z0-9-]*)\s*$", front)
    description = re.search(r"(?m)^description:\s*(.+)$", front)
    if not name or not description:
        print("FAIL: name/description required")
        return 1
    if len(name.group(1)) > 64 or len(description.group(1)) > 200:
        print("FAIL: name or description too long")
        return 1
    if name.group(1) != root.name:
        print("FAIL: folder name mismatch")
        return 1
    for rel in ["references/investment-framework.md", "references/source-policy.md", "references/investment-memo-template.md", "references/mcp-tools.md", "references/local-llm-system-prompt.md"]:
        if not (root / rel).is_file():
            print("FAIL: missing " + rel)
            return 1
    print("PASS: " + name.group(1) + " manifest and references validated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
