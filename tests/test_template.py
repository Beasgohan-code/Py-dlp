"""Tests for template path formatting."""

import unittest
from pydlp.core.template import TemplateFormatter
from pydlp.core.types import MediaInfo


class TestTemplateFormatter(unittest.TestCase):
    def test_default_template(self):
        formatter = TemplateFormatter("%(title)s [%(id)s].%(ext)s")
        info = MediaInfo(
            id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            extractor="youtube",
            extractor_key="Youtube",
            ext="mp4",
        )
        res = formatter.format(info)
        self.assertEqual(res, "Never Gonna Give You Up [dQw4w9WgXcQ].mp4")

    def test_autonumber_and_uploader(self):
        formatter = TemplateFormatter("%(autonumber)03d - %(uploader)s - %(title)s.%(ext)s")
        info = {
            "id": "123",
            "title": "My Track",
            "uploader": "Rick Astley",
            "ext": "mp3",
        }
        res = formatter.format(info)
        self.assertEqual(res, "001 - Rick Astley - My Track.mp3")

    def test_sanitization(self):
        formatter = TemplateFormatter("%(title)s.%(ext)s")
        info = {
            "id": "123",
            "title": "Invalid/File:Name*With?Illegal<Chars>|And\"Quotes",
            "ext": "mp4",
        }
        res = formatter.format(info)
        self.assertNotIn(":", res)
        self.assertNotIn("*", res)
        self.assertNotIn("?", res)
        self.assertNotIn("<", res)
        self.assertNotIn(">", res)
        self.assertNotIn("|", res)
        self.assertNotIn('"', res)


if __name__ == "__main__":
    unittest.main()
