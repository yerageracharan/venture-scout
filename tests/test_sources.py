import unittest
from venture_scout.sources.google_news import _amount_usd, _company_from_title
from venture_scout.sources.sec_edgar import _form_d_xml_url


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
