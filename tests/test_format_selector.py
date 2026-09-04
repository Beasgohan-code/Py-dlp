"""Tests for format selection DSL."""

import unittest
from pydlp.core.format_selector import FormatSelector
from pydlp.core.types import MediaFormat, MediaInfo


class TestFormatSelector(unittest.TestCase):
    def setUp(self):
        self.formats = [
            MediaFormat(format_id="137", url="http://test/1080p.mp4", ext="mp4", height=1080, width=1920, fps=30, vcodec="avc1", acodec="none", tbr=3000),
            MediaFormat(format_id="136", url="http://test/720p.mp4", ext="mp4", height=720, width=1280, fps=30, vcodec="avc1", acodec="none", tbr=1500),
            MediaFormat(format_id="18", url="http://test/360p.mp4", ext="mp4", height=360, width=640, fps=30, vcodec="avc1", acodec="mp4a", tbr=600),
            MediaFormat(format_id="140", url="http://test/audio.m4a", ext="m4a", height=None, width=None, fps=None, vcodec="none", acodec="mp4a", abr=128),
        ]
        self.info = MediaInfo(
            id="test12345",
            title="Test Video",
            extractor="test",
            extractor_key="Test",
            formats=self.formats,
        )

    def test_best_video_plus_best_audio(self):
        selector = FormatSelector("bestvideo+bestaudio")
        selected = selector.select_formats(self.info)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0].format_id, "137")
        self.assertEqual(selected[1].format_id, "140")

    def test_filter_resolution(self):
        selector = FormatSelector("bestvideo[height<=720]+bestaudio/best")
        selected = selector.select_formats(self.info)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0].format_id, "136")
        self.assertEqual(selected[1].format_id, "140")

    def test_best_single(self):
        selector = FormatSelector("best")
        selected = selector.select_formats(self.info)
        self.assertEqual(len(selected), 1)
        # Prefers complete video+audio format (18)
        self.assertEqual(selected[0].format_id, "18")

    def test_exact_format_id(self):
        selector = FormatSelector("136+140")
        selected = selector.select_formats(self.info)
        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0].format_id, "136")
        self.assertEqual(selected[1].format_id, "140")

    def test_best_audio_only(self):
        selector = FormatSelector("bestaudio")
        selected = selector.select_formats(self.info)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].format_id, "140")


if __name__ == "__main__":
    unittest.main()
