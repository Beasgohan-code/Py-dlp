"""Tests for Python API and PyDLP core workflow."""

import unittest
from pydlp import PyDLP, AsyncPyDLP
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo


class TestPyDLPAPI(unittest.TestCase):
    def test_instantiation(self):
        dlp = PyDLP({"simulate": True, "quiet": True})
        self.assertIsNotNone(dlp)
        self.assertIsNotNone(dlp.http)
        self.assertIsNotNone(dlp.format_selector)
        self.assertIsNotNone(dlp.template_formatter)

    def test_direct_url_extraction(self):
        dlp = PyDLP({"simulate": True, "quiet": True})
        info = dlp.extract_info("https://example.com/videos/awesome_movie.mp4", download=False)
        self.assertIsNotNone(info)
        self.assertEqual(info.ext, "mp4")
        self.assertGreaterEqual(len(info.formats), 1)

    def test_progress_hook(self):
        events = []
        dlp = PyDLP({"simulate": True, "quiet": True})
        dlp.add_progress_hook(lambda p: events.append(p))
        dlp.progress_dispatcher.dispatch(DownloadProgress(status="finished", downloaded_bytes=1000))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].status, "finished")


if __name__ == "__main__":
    unittest.main()
