"""Tests for CLI options and arguments."""

import unittest
from pydlp.options import build_arg_parser, parse_cli_args


class TestCli(unittest.TestCase):
    def test_parse_args_defaults(self):
        parsed, opts = parse_cli_args(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
        self.assertEqual(opts["urls"], ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
        self.assertEqual(opts["format"], "bestvideo+bestaudio/best")
        self.assertEqual(opts["outtmpl"], "%(title)s [%(id)s].%(ext)s")
        self.assertFalse(opts["extract_audio"])

    def test_audio_extraction_flags(self):
        parsed, opts = parse_cli_args(["-x", "--audio-format", "mp3", "--audio-quality", "320k", "https://example.com/audio"])
        self.assertTrue(opts["extract_audio"])
        self.assertEqual(opts["audio_format"], "mp3")
        self.assertEqual(opts["audio_quality"], "320k")

    def test_concurrent_fragments_flag(self):
        parsed, opts = parse_cli_args(["-N", "8", "https://example.com/video.mp4"])
        self.assertEqual(opts["concurrent_fragments"], 8)

    def test_custom_headers(self):
        parsed, opts = parse_cli_args(["--add-header", "Authorization: Bearer token123", "https://example.com/video.mp4"])
        self.assertIn("Authorization", opts["headers"])
        self.assertEqual(opts["headers"]["Authorization"], "Bearer token123")


if __name__ == "__main__":
    unittest.main()
