"""Tests for AI transcript analyzer, auto-chapters, and summary generation."""

import unittest
from pydlp.core.ai_summary import TranscriptAnalyzer


class TestAISummary(unittest.TestCase):
    def setUp(self):
        self.vtt_sample = """WEBVTT

00:00:01.000 --> 00:00:05.000
Welcome everyone. First, we are going to talk about python development.

00:01:10.000 --> 00:01:15.000
Next, we will explore high-speed media downloading and network optimizations.

00:02:30.000 --> 00:02:35.000
In conclusion, always remember that architecture matters.
"""

    def test_analyzer_cues_and_chapters(self):
        analyzer = TranscriptAnalyzer(self.vtt_sample)
        self.assertEqual(len(analyzer.cues), 3)

        chapters = analyzer.generate_auto_chapters(min_gap_seconds=30.0)
        self.assertGreaterEqual(len(chapters), 2)
        self.assertEqual(chapters[0].title, "Introduction")

    def test_summary_markdown_generation(self):
        analyzer = TranscriptAnalyzer(self.vtt_sample)
        summary = analyzer.generate_summary("Advanced Python Lecture", duration=180.0)
        self.assertIn("# 📝 Media Summary: Advanced Python Lecture", summary)
        self.assertIn("## 📌 Key Takeaways & Highlights", summary)
        self.assertIn("## ⏱️ Auto-Generated Timestamps & Topics", summary)


if __name__ == "__main__":
    unittest.main()
