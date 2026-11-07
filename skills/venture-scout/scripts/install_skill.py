#!/usr/bin/env python3
"""Install Venture Scout into common Agent Skills directories."""
from pathlib import Path
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description="Install Venture Scout Agent Skill")
    parser.add_argument("--target", choices=["claude-code", "codex", "both"], default="both")
    parser.add_argument("--scope", choices=["user", "project"], default="user")
    parser.add_argument("--project", type=Path, default=Path.cwd())
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    home = Path.home()
    destinations = []
    if args.target in ("claude-code", "both"):
        base = home / ".claude" / "skills" if args.scope == "user" else args.project / ".claude" / "skills"
        destinations.append(base / "venture-scout")
    if args.target in ("codex", "both"):
        base = home / ".agents" / "skills" if args.scope == "user" else args.project / ".agents" / "skills"
        destinations.append(base / "venture-scout")
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        print(f"Installed: {destination}")
    print("Restart the host if the skill is not discovered automatically.")

if __name__ == "__main__":
    main()
