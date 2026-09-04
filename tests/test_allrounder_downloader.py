import unittest
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.downloader.allrounder import AllRounderDownloader
from pydlp.downloader.dash import DashDownloader
from pydlp.downloader.external import ExternalDownloader
from pydlp.downloader.hls import HlsDownloader
from pydlp.downloader.hls_live import HLSLiveDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.resumable import ResumableDownloader
from pydlp.downloader.turbo import TurboDownloader
from pydlp.downloader.websocket import WebSocketDownloader


class TestAllRounderDownloader(unittest.TestCase):
    def setUp(self):
        self.http = HttpClient()

    def test_hls_stream_routing(self):
        downloader = AllRounderDownloader(self.http, {})
        fmt = MediaFormat(format_id="hls-1080p", url="https://example.com/playlist.m3u8", protocol="m3u8_native", ext="mp4")
        info = MediaInfo(id="123", title="Test", webpage_url="https://example.com/watch", extractor="generic", extractor_key="generic")
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, HlsDownloader)

    def test_dash_stream_routing(self):
        downloader = AllRounderDownloader(self.http, {})
        fmt = MediaFormat(format_id="dash-1080p", url="https://example.com/manifest.mpd", protocol="dash", ext="mp4")
        info = MediaInfo(id="123", title="Test", webpage_url="https://example.com/watch", extractor="generic", extractor_key="generic")
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, DashDownloader)

    def test_turbo_routing(self):
        downloader = AllRounderDownloader(self.http, {"turbo": True})
        fmt = MediaFormat(format_id="direct", url="https://example.com/video.mp4", ext="mp4")
        info = MediaInfo(id="123", title="Test", webpage_url="https://example.com/watch", extractor="generic", extractor_key="generic")
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, TurboDownloader)

    def test_resumable_routing(self):
        downloader = AllRounderDownloader(self.http, {"continue_dl": True})
        fmt = MediaFormat(format_id="direct", url="https://example.com/video.mp4", ext="mp4")
        info = MediaInfo(id="123", title="Test", webpage_url="https://example.com/watch", extractor="generic", extractor_key="generic")
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, ResumableDownloader)

    def test_live_hls_routing(self):
        downloader = AllRounderDownloader(self.http, {"live_record_duration": 60})
        fmt = MediaFormat(format_id="hls-live", url="https://example.com/live.m3u8", protocol="m3u8", ext="mp4")
        info = MediaInfo(id="123", title="Live Test", webpage_url="https://example.com/live", extractor="generic", extractor_key="generic", is_live=True)
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, HLSLiveDownloader)

    def test_external_downloader_routing(self):
        downloader = AllRounderDownloader(self.http, {"external_downloader": "curl"})
        fmt = MediaFormat(format_id="direct", url="https://example.com/video.mp4", ext="mp4")
        info = MediaInfo(id="123", title="Test", webpage_url="https://example.com/watch", extractor="generic", extractor_key="generic")
        selected = downloader._select_downloader(fmt, info)
        self.assertIsInstance(selected, ExternalDownloader)


if __name__ == "__main__":
    unittest.main()
