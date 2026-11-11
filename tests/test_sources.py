import unittest
from venture_scout.sources.google_news import _amount_usd, _company_from_title
from datetime import date

from venture_scout.sources.sec_edgar import _form_d_xml_url, discover_form_d


class SourceParsingTests(unittest.TestCase):
    def test_parse_million_amount(self):
        self.assertEqual(_amount_usd("Raises $4.3 million seed round"), 4_300_000)

    def test_parse_compact_amount(self):
        self.assertEqual(_amount_usd("Secures $7.5M in seed funding"), 7_500_000)

    def test_parse_company_from_headline(self):
        self.assertEqual(_company_from_title("Example AI raises $6M seed round"), "Example AI")

    def test_sec_master_index_path_to_xml_url(self):
        filename = "edgar/data/0002149558/0002149558-26-000001.txt"
        self.assertEqual(_form_d_xml_url(filename), "https://www.sec.gov/Archives/edgar/data/2149558/000214955826000001/primary_doc.xml")


class SecDiscoveryInputTests(unittest.TestCase):
    def test_max_filings_must_be_a_bounded_positive_integer(self):
        start, end = date(2026, 1, 1), date(2026, 1, 31)
        for value in (0, -1, 1001, True, 1.5):
            with self.subTest(max_filings=value):
                with self.assertRaisesRegex(ValueError, "max_filings"):
                    discover_form_d(start, end, "Research Tool contact@example.com", max_filings=value)

    def test_rejects_reversed_date_window_before_network_access(self):
        with self.assertRaisesRegex(ValueError, "start_date"):
            discover_form_d(date(2026, 2, 1), date(2026, 1, 1), "Research Tool contact@example.com")

    def test_requires_date_objects(self):
        with self.assertRaisesRegex(TypeError, "datetime.date"):
            discover_form_d("2026-01-01", date(2026, 1, 31), "Research Tool contact@example.com")
