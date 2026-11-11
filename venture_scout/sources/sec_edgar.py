from __future__ import annotations
import re
import time
from pathlib import PurePosixPath
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

BASE = "https://www.sec.gov/Archives/edgar/daily-index"


def _tag_text(root: ET.Element, suffix: str) -> str:
    for node in root.iter():
        if node.tag.split("}")[-1] == suffix and node.text:
            return node.text.strip()
    return ""


def _quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def _form_d_xml_url(filename: str) -> str:
    """Translate a master.idx filename into the Form D primary XML URL."""
    parts = PurePosixPath(filename.strip()).parts
    try:
        data_index = parts.index("data")
        cik = str(int(parts[data_index + 1]))
        accession = PurePosixPath(parts[-1]).stem
    except (ValueError, IndexError) as exc:
        raise ValueError(f"Unexpected SEC master-index filename: {filename}") from exc
    if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession):
        raise ValueError(f"Unexpected SEC accession number: {accession}")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/primary_doc.xml"


def _fetch(url: str, user_agent: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "text/plain, application/xml, */*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(25_000_000)


def discover_form_d(start_date: date, end_date: date, user_agent: str, max_filings: int = 100) -> list[dict[str, Any]]:
    """Find Form D filings from SEC quarterly master indexes, then inspect primary XML.

    Form D records an exempt securities offering. It is not proof of a priced seed round,
    a venture round label, or the final amount raised. Keep it as a separate signal.
    """
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        raise TypeError("start_date and end_date must be datetime.date values")
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")
    if isinstance(max_filings, bool) or not isinstance(max_filings, int) or not 1 <= max_filings <= 1000:
        raise ValueError("max_filings must be an integer between 1 and 1000")
    if not isinstance(user_agent, str) or not user_agent.strip() or "@" not in user_agent:
        raise ValueError("Set SEC_USER_AGENT to a descriptive app name and contact email per SEC fair-access guidance.")
    indexes: list[tuple[int, int]] = []
    cursor = date(start_date.year, start_date.month, 1)
    while cursor <= end_date:
        pair = (cursor.year, _quarter(cursor))
        if pair not in indexes:
            indexes.append(pair)
        if cursor.month in (10, 11, 12):
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + (3 - ((cursor.month - 1) % 3)), 1)
    rows: list[dict[str, Any]] = []
    for year, quarter in indexes:
        url = f"{BASE}/{year}/QTR{quarter}/master.idx"
        raw = _fetch(url, user_agent).decode("latin-1", errors="replace")
        for line in raw.splitlines():
            if "|" not in line or line.startswith("CIK|"):
                continue
            parts = line.split("|")
            if len(parts) != 5 or parts[2].upper() != "D":
                continue
            try:
                filed = date.fromisoformat(parts[3])
                filename = parts[4].strip()
            except Exception:
                continue
            if start_date <= filed <= end_date:
                rows.append({"cik": parts[0].strip(), "issuer_name_index": parts[1].strip(), "filed": filed.isoformat(), "filename": filename})
    results: list[dict[str, Any]] = []
    for row in rows[-max_filings:]:
        xml_url = _form_d_xml_url(row["filename"])
        try:
            xml = _fetch(xml_url, user_agent)
            root = ET.fromstring(xml)
            city = _tag_text(root, "city")
            state = _tag_text(root, "stateOrCountry")
            issuer = _tag_text(root, "issuerName") or row["issuer_name_index"]
            total_offering = _tag_text(root, "totalOfferingAmount")
            total_sold = _tag_text(root, "totalAmountSold")
            industry = _tag_text(root, "industryGroupType")
            entity_type = _tag_text(root, "entityType")
            investment_fund_type = _tag_text(root, "investmentFundType")
            first_sale_date = _tag_text(root, "dateOfFirstSale")
            results.append({
                **row,
                "issuer_name": issuer,
                "city": city,
                "state": state,
                "industry": industry,
                "entity_type": entity_type,
                "investment_fund_type": investment_fund_type,
                "date_of_first_sale": first_sale_date,
                "total_offering_amount_usd": total_offering,
                "total_amount_sold_at_filing_usd": total_sold,
                "filing_url": xml_url,
                "evidence_type": "SEC Form D exempt-offering notice; not necessarily seed funding",
            })
        except Exception as exc:
            results.append({**row, "error": str(exc), "filing_url": xml_url})
        time.sleep(0.12)
    return results
