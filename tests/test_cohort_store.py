import json
import tempfile
import unittest
from pathlib import Path
from venture_scout.models import Company, DimensionEvidence
from venture_scout.store import Store
from venture_scout.cohort import analyse_cohort, analyse_outcomes


class CohortAndStoreTests(unittest.TestCase):
    def test_seed_data_loads(self):
        path = Path(__file__).resolve().parents[1] / "data" / "research_seeds.json"
        companies = [Company.from_dict(x) for x in json.loads(path.read_text(encoding="utf-8"))]
        self.assertEqual(len(companies), 14)
        self.assertTrue(all(c.sources for c in companies))

    def test_store_round_trip_keeps_evidence_and_outcomes(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(Path(folder) / "test.db")
            company = Company(name="TestCo", outcome_status="Follow-on round", follow_on_round_amount_usd=2_000_000,
                              dimensions={"market": DimensionEvidence(rating=4, evidence="Customer interviews")})
            store.upsert(company)
            loaded = store.get(company.company_id)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.outcome_status, "Follow-on round")
            self.assertEqual(loaded.dimensions["market"].rating, 4)

    def test_outcome_analysis_is_empty_until_labels_exist(self):
        result = analyse_outcomes([Company(name="A"), Company(name="B")])
        self.assertEqual(result["labelled_companies"], 0)
        self.assertEqual(result["outcome_counts"], [])

    def test_cohort_counts_verified_rounds_only(self):
        companies = [
            Company(name="A", sector="AI", round_amount_usd=2_000_000, investors=["Fund A"], funding_evidence_status="announced_verified"),
            Company(name="B", sector="AI", round_amount_usd=4_000_000, investors=["Fund A", "Fund B"], funding_evidence_status="announced_verified"),
            Company(name="C", sector="AI", round_amount_usd=99_000_000, investors=["Fund X"], funding_evidence_status="announced_unverified"),
        ]
        result = analyse_cohort(companies)
        self.assertEqual(result["funded_records"], 2)
        self.assertEqual(result["unverified_funding_leads"], 1)
        self.assertEqual(result["median_round_usd"], 3_000_000)
        self.assertEqual(result["investor_counts"][0], ("Fund A", 2))
