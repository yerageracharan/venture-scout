from __future__ import annotations
import argparse
import json
from pathlib import Path
from .models import Company
from .store import Store
from .scoring import score_company
from .memo import build_memo


def main() -> None:
    parser = argparse.ArgumentParser(description="Venture Scout research utility")
    parser.add_argument("--db", default="data/venture_scout.db")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="Load the sourced starter cohort if the database is empty")
    sub.add_parser("list", help="List companies in the local database")
    memo_parser = sub.add_parser("memo", help="Write a deterministic memo for a company")
    memo_parser.add_argument("company_id")
    memo_parser.add_argument("--out", default="investment-memo.md")
    args = parser.parse_args()
    store = Store(args.db)
    if args.command == "seed":
        if store.get_all():
            print("Database is not empty; no seed records added.")
            return
        records = json.loads(Path("data/research_seeds.json").read_text(encoding="utf-8"))
        for row in records:
            store.upsert(Company.from_dict(row))
        print(f"Loaded {len(records)} starter records.")
    elif args.command == "list":
        for company in store.get_all():
            result = score_company(company)
            print(f"{company.company_id} | {company.name} | {company.sector} | {company.stage} | {result['verdict']}")
    elif args.command == "memo":
        company = store.get(args.company_id)
        if not company:
            raise SystemExit(f"Unknown company_id: {args.company_id}")
        Path(args.out).write_text(build_memo(company), encoding="utf-8")
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
