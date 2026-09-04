"""Unit tests for Universal Extractor 2.0, getters, queries, and execution flags."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pydlp.core.types import MediaFormat, MediaInfo, MediaSubtitle
from pydlp.extractor.generic import UniversalExtractor
from pydlp.pydlp import PyDLP


class TestUniversalAndGetters(unittest.TestCase):
    """Test suite for universal extraction heuristics and yt-dlp getter compatibility."""

    def test_universal_extractor_html5_and_jsonld(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Awesome Universal Video</title>
            <meta property="og:title" content="Awesome Universal Video OG">
            <meta property="og:description" content="00:00 Intro\n01:30 Chapter One\n05:00 Ending">
            <meta property="og:image" content="https://example.com/thumb.jpg">
            <script type="application/ld+json">
            {
                "@type": "VideoObject",
                "name": "JSON-LD Title",
                "contentUrl": "https://example.com/media/stream.m3u8",
                "duration": "PT3M30S"
            }
            </script>
        </head>
        <body>
            <video src="https://example.com/video.mp4">
                <track src="https://example.com/sub_en.vtt" srclang="en" kind="subtitles">
            </video>
        </body>
        </html>
        """
        ie = UniversalExtractor()
        with patch.object(ie, "_download_webpage", return_value=sample_html), \
             patch.object(ie, "_extract_m3u8_formats", return_value=[MediaFormat(format_id="hls-1080p", url="https://example.com/media/stream.m3u8", ext="mp4")]):
            info = ie.extract("https://example.com/watch")
            self.assertEqual(info.title, "JSON-LD Title")
            self.assertEqual(info.duration, 210.0)
            self.assertTrue(len(info.formats) >= 2)
            self.assertIn("en", info.subtitles)
            self.assertEqual(len(info.chapters), 3)
            self.assertEqual(info.chapters[1].title, "Chapter One")

    def test_pydlp_getter_flags(self):
        dummy_info = MediaInfo(
            id="vid123",
            title="Sample Title",
            duration=120.0,
            url="https://example.com/direct.mp4",
            formats=[MediaFormat(format_id="best", url="https://example.com/direct.mp4", ext="mp4")],
        )

        dlp = PyDLP({"simulate": True, "get_title": True, "quiet": True})
        with patch.object(dlp, "extract_info", return_value=dummy_info):
            self.assertTrue(dlp.params.get("get_title"))

        dlp_print = PyDLP({"simulate": True, "print_tmpl": "%(title)s [%(id)s]", "quiet": True})
        formatted = dlp_print.template_formatter.format(dlp_print.params["print_tmpl"], dummy_info)
        self.assertEqual(formatted, "Sample Title [vid123]")


if __name__ == "__main__":
    unittest.main()
