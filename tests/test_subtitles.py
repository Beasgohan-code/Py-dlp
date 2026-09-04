"""Tests for subtitle format converter."""

import unittest
from pydlp.postprocessor.subtitles import ttml_to_srt, vtt_to_srt


class TestSubtitles(unittest.TestCase):
    def test_vtt_to_srt(self):
        vtt_sample = """WEBVTT

00:00:01.000 --> 00:00:04.000
Hello world!

00:00:05.500 --> 00:00:08.200
This is a second subtitle line.
"""
        srt = vtt_to_srt(vtt_sample)
        self.assertIn("1", srt)
        self.assertIn("00:00:01,000 --> 00:00:04,000", srt)
        self.assertIn("Hello world!", srt)
        self.assertIn("2", srt)
        self.assertIn("00:00:05,500 --> 00:00:08,200", srt)
        self.assertIn("This is a second subtitle line.", srt)

    def test_ttml_to_srt(self):
        ttml_sample = """<tt>
          <body>
            <div>
              <p begin="00:00:01.000" end="00:00:04.000">TTML caption text</p>
            </div>
          </body>
        </tt>"""
        srt = ttml_to_srt(ttml_sample)
        self.assertIn("1", srt)
        self.assertIn("00:00:01,000 --> 00:00:04,000", srt)
        self.assertIn("TTML caption text", srt)


if __name__ == "__main__":
    unittest.main()
