from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from .models import Company


class Store:
    def __init__(self, path: str | Path = "data/venture_scout.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS companies (company_id TEXT PRIMARY KEY, name TEXT NOT NULL, payload TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)")

    def upsert(self, company: Company) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO companies(company_id,name,payload,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP) ON CONFLICT(company_id) DO UPDATE SET name=excluded.name,payload=excluded.payload,updated_at=CURRENT_TIMESTAMP", (company.company_id, company.name, json.dumps(company.to_dict())))

    def get_all(self) -> list[Company]:
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM companies ORDER BY name COLLATE NOCASE").fetchall()
        return [Company.from_dict(json.loads(row["payload"])) for row in rows]

    def get(self, company_id: str) -> Company | None:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM companies WHERE company_id=?", (company_id,)).fetchone()
        return Company.from_dict(json.loads(row["payload"])) if row else None

    def delete(self, company_id: str) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM companies WHERE company_id=?", (company_id,))
