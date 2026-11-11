import unittest

from venture_scout.models import Company, DimensionEvidence, DIMENSIONS
from venture_scout.scoring import score_company, diligence_gaps


class ScoringTests(unittest.TestCase):
    def test_empty_evidence_is_insufficient_not_zero_score(self):
        result = score_company(Company(name="Unknown Co"))
        self.assertIsNone(result["score"])
        self.assertEqual(result["coverage"], 0)
        self.assertEqual(result["verdict"], "INSUFFICIENT EVIDENCE")

    def test_full_five_scores_equal_100_and_deep_dive(self):
        dimensions = {key: DimensionEvidence(rating=5, evidence="Evidence logged") for key in DIMENSIONS}
        result = score_company(Company(name="Strong Co", dimensions=dimensions))
        self.assertEqual(result["score"], 100.0)
        self.assertEqual(result["coverage"], 100)
        self.assertEqual(result["verdict"], "DEEP DIVE")

    def test_missing_dimensions_reduce_coverage_not_raw_score(self):
        keys = list(DIMENSIONS)[:4]
        dimensions = {key: DimensionEvidence(rating=4, evidence="Evidence logged") for key in keys}
        result = score_company(Company(name="Partial Co", dimensions=dimensions))
        self.assertEqual(result["coverage"], sum(DIMENSIONS[k]["weight"] for k in keys))
        self.assertEqual(result["score"], 80.0)
        self.assertEqual(result["verdict"], "INSUFFICIENT EVIDENCE")

    def test_rating_without_written_evidence_is_not_counted(self):
        dimensions = {key: DimensionEvidence(rating=5, evidence="") for key in DIMENSIONS}
        result = score_company(Company(name="Unsupported Co", dimensions=dimensions))
        self.assertIsNone(result["score"])
        self.assertEqual(result["coverage"], 0)

    def test_score_rejects_invalid_rating(self):
        dimensions = {key: DimensionEvidence(rating=6, evidence="Invalid") for key in DIMENSIONS}
        result = score_company(Company(name="Invalid Co", dimensions=dimensions))
        self.assertIsNone(result["score"])
        self.assertEqual(result["coverage"], 0)

    def test_diligence_gaps_surface_missing_critical_evidence(self):
        gaps = diligence_gaps(Company(name="Gap Co"))
        self.assertTrue(any("Founder-market fit" in gap for gap in gaps))
        self.assertTrue(any("Customer / usage evidence" in gap for gap in gaps))
        self.assertTrue(any("No source URLs" in gap for gap in gaps))

    def test_non_integer_ratings_are_not_coerced(self):
        for invalid in ("5", 5.0, 4.5, True, False):
            dimensions = {key: DimensionEvidence(rating=invalid, evidence="Evidence logged") for key in DIMENSIONS}
            result = score_company(Company(name="Imported Co", dimensions=dimensions))
            self.assertIsNone(result["score"], msg=f"Unexpectedly accepted {invalid!r}")
            self.assertEqual(result["coverage"], 0)

    def test_malformed_evidence_is_treated_as_missing_not_crashing(self):
        dimensions = {key: DimensionEvidence(rating=5, evidence=None) for key in DIMENSIONS}
        result = score_company(Company(name="Malformed Co", dimensions=dimensions))
        self.assertIsNone(result["score"])
        self.assertEqual(result["coverage"], 0)

    def test_invalid_ratings_appear_as_unassessed_gaps(self):
        dimensions = {"market": DimensionEvidence(rating=6, evidence="Some text")}
        gaps = diligence_gaps(Company(name="Invalid Co", dimensions=dimensions))
        self.assertTrue(any("Unassessed: Market size & urgency" in gap for gap in gaps))


if __name__ == "__main__":
    unittest.main()
