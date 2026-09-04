"""Tests for SponsorBlock segment logic."""

import unittest
from pydlp.core.sponsorblock import SponsorSegment


class TestSponsorBlock(unittest.TestCase):
    def test_segment_properties(self):
        seg = SponsorSegment(category="sponsor", start_time=10.5, end_time=35.0, uuid="abc-123")
        self.assertEqual(seg.category, "sponsor")
        self.assertEqual(seg.duration, 24.5)
        d = seg.to_dict()
        self.assertEqual(d["category"], "sponsor")
        self.assertEqual(d["start_time"], 10.5)


if __name__ == "__main__":
    unittest.main()
