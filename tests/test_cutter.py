"""Tests for time-range cutter parser."""

import unittest
from pydlp.postprocessor.cutter import parse_time_range


class TestCutter(unittest.TestCase):
    def test_parse_time_range_formats(self):
        start, end = parse_time_range("*01:00-03:30")
        self.assertEqual(start, 60.0)
        self.assertEqual(end, 210.0)

        start2, end2 = parse_time_range("00:30-01:15")
        self.assertEqual(start2, 30.0)
        self.assertEqual(end2, 75.0)

        start3, end3 = parse_time_range("45-120")
        self.assertEqual(start3, 45.0)
        self.assertEqual(end3, 120.0)


if __name__ == "__main__":
    unittest.main()
