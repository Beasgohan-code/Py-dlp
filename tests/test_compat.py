import unittest
from unittest.mock import MagicMock
from pydlp.compat.yt_dlp.extractor.common import InfoExtractor
from pydlp.compat.yt_dlp.utils import traverse_obj, js_to_json, unified_strdate
from pydlp.core.types import MediaInfo

class SampleYtDlpStyleIE(InfoExtractor):
    IE_NAME = "sample_ytdl_site"
    _VALID_URL = r"https?://sample-ytdl\.com/watch/(?P<id>[a-zA-Z0-9]+)"

    def _real_extract(self, url: str) -> dict:
        video_id = self._match_id(url)
        return {
            "id": video_id,
            "title": "Sample Title",
            "formats": [
                {"format_id": "1080p", "url": f"https://sample-ytdl.com/{video_id}.mp4", "width": 1920, "height": 1080, "ext": "mp4"}
            ],
            "uploader": "Test Channel",
            "upload_date": unified_strdate("2026-09-04"),
            "duration": 120,
        }

class TestCompat(unittest.TestCase):
    def test_traverse_obj(self):
        data = {"nested": {"items": [{"name": "target_val"}]}}
        self.assertEqual(traverse_obj(data, ("nested", "items", 0, "name")), "target_val")
        self.assertIsNone(traverse_obj(data, ("nested", "nonexistent")))

    def test_js_to_json(self):
        js = "{ key: 'value', count: 42, }"
        parsed = js_to_json(js)
        self.assertIn('"key": "value"', parsed)
        self.assertIn('"count": 42', parsed)

    def test_ytdl_style_extractor_execution(self):
        ie = SampleYtDlpStyleIE()
        res = ie.extract("https://sample-ytdl.com/watch/abc1234")
        self.assertIsInstance(res, MediaInfo)
        self.assertEqual(res.id, "abc1234")
        self.assertEqual(res.title, "Sample Title")
        self.assertEqual(len(res.formats), 1)
        self.assertEqual(res.formats[0].height, 1080)
        self.assertEqual(res.upload_date, "20260904")

if __name__ == "__main__":
    unittest.main()
