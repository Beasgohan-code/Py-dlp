"""Comprehensive test suite for Py-dlp advanced features."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pydlp.core.bookmarks import BookmarkImporter
from pydlp.core.interactive import InteractiveSelector
from pydlp.core.notifications import NotificationManager
from pydlp.core.proxy_pool import ProxyPool
from pydlp.core.ratelimit import RateLimiter, parse_rate_limit
from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.watcher import WatcherDaemon
from pydlp.extractor.torrent import TorrentExtractor
from pydlp.postprocessor.enhancer import MediaEnhancerPostProcessor


class TestAdvancedFeatures(unittest.TestCase):
    """Unit tests for newly added advanced capabilities."""

    def test_parse_rate_limit(self):
        self.assertIsNone(parse_rate_limit(None))
        self.assertEqual(parse_rate_limit(500), 500.0)
        self.assertEqual(parse_rate_limit("500"), 500.0)
        self.assertEqual(parse_rate_limit("1K"), 1024.0)
        self.assertEqual(parse_rate_limit("2KB"), 2048.0)
        self.assertEqual(parse_rate_limit("5M"), 5 * 1024 * 1024.0)
        self.assertEqual(parse_rate_limit("1.5MB/s"), 1.5 * 1024 * 1024.0)
        self.assertEqual(parse_rate_limit("1G"), 1024 * 1024 * 1024.0)

    def test_rate_limiter_throttling(self):
        limiter = RateLimiter(bytes_per_second=1000000.0)
        # Consuming small amount should not raise
        limiter.throttle(500)
        self.assertTrue(limiter.bucket <= limiter.capacity)

    def test_interactive_selector_resolution(self):
        fmts = [
            MediaFormat(format_id="137", url="https://example.com/1080.mp4", ext="mp4", width=1920, height=1080, vcodec="h264", acodec="none"),
            MediaFormat(format_id="140", url="https://example.com/audio.m4a", ext="m4a", acodec="aac", vcodec="none", abr=128),
            MediaFormat(format_id="22", url="https://example.com/720.mp4", ext="mp4", width=1280, height=720, vcodec="h264", acodec="aac"),
        ]
        selector = InteractiveSelector(color=False)

        # Selection by number
        res1 = selector._resolve_choice("1", fmts)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].format_id, "137")

        # Selection by format_id
        res2 = selector._resolve_choice("22", fmts)
        self.assertEqual(len(res2), 1)
        self.assertEqual(res2[0].format_id, "22")

        # Selection by combo '+'
        res3 = selector._resolve_choice("137+140", fmts)
        self.assertEqual(len(res3), 2)
        self.assertEqual(res3[0].format_id, "137")
        self.assertEqual(res3[1].format_id, "140")

        # Selection by resolution
        res4 = selector._resolve_choice("1080p", fmts)
        self.assertEqual(len(res4), 1)
        self.assertEqual(res4[0].format_id, "137")

        # Selection by audio keyword
        res5 = selector._resolve_choice("audio", fmts)
        self.assertEqual(len(res5), 1)
        self.assertEqual(res5[0].format_id, "140")

    def test_proxy_pool_rotation_and_health(self):
        pool = ProxyPool("http://proxy1:8080,http://proxy2:8080", mode="round-robin")
        self.assertEqual(pool.get_proxy(), "http://proxy1:8080")
        self.assertEqual(pool.get_proxy(), "http://proxy2:8080")
        self.assertEqual(pool.get_proxy(), "http://proxy1:8080")

        # Report failure
        for _ in range(5):
            pool.report_failure("http://proxy1:8080")
        # proxy1 disabled, proxy2 active
        self.assertEqual(pool.get_proxy(), "http://proxy2:8080")

    def test_bookmark_importer(self):
        sample_html = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <HTML>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
            <DT><A HREF="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Rick Astley</A>
            <DT><A HREF="https://vimeo.com/76979871">The Mountain</A>
        </DL><p>
        </HTML>
        """
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(sample_html)
            f_path = f.name

        try:
            urls = BookmarkImporter.parse_html_bookmarks(f_path)
            self.assertEqual(len(urls), 2)
            self.assertIn("https://www.youtube.com/watch?v=dQw4w9WgXcQ", urls)
            self.assertIn("https://vimeo.com/76979871", urls)
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_m3u_playlist_importer(self):
        sample_m3u = """#EXTM3U
#EXTINF:-1 tvg-id="stream1",Stream 1
https://example.com/live/stream1.m3u8
#EXTINF:-1 tvg-id="stream2",Stream 2
https://example.com/vod/video2.mp4
"""
        with tempfile.NamedTemporaryFile("w", suffix=".m3u", delete=False) as f:
            f.write(sample_m3u)
            f_path = f.name

        try:
            urls = BookmarkImporter.parse_m3u_playlist(f_path)
            self.assertEqual(len(urls), 2)
            self.assertEqual(urls[0], "https://example.com/live/stream1.m3u8")
            self.assertEqual(urls[1], "https://example.com/vod/video2.mp4")
        finally:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_torrent_extractor(self):
        extractor = TorrentExtractor(MagicMock(), {})
        magnet_url = "magnet:?xt=urn:btih:c12fe1c06bba254a9dc9f519b335377f7da443f3&dn=Sample+Media+Video&tr=http%3A%2F%2Ftracker.example.com%2Fannounce"
        self.assertTrue(extractor._match_url(magnet_url))

        info = extractor._real_extract(magnet_url)
        self.assertEqual(info.title, "Sample Media Video")
        self.assertEqual(info.id, "c12fe1c06bba254a9dc9f519b335377f7da443f3")
        self.assertEqual(len(info.formats), 1)
        self.assertEqual(info.formats[0].format_id, "torrent-stream")

    def test_media_enhancer_postprocessor_config(self):
        opts = {
            "audio_loudnorm": True,
            "audio_pitch": 1.1,
            "audio_tempo": 1.25,
            "video_speed": 1.5,
            "video_denoise": True,
            "reencode_codec": "hevc",
        }
        pp = MediaEnhancerPostProcessor(opts)
        self.assertTrue(pp.is_needed)

    def test_notification_manager(self):
        opts = {
            "notify_discord": "https://discord.com/api/webhooks/test",
            "notify_telegram": "123456:ABC-DEF:987654321",
            "notify_webhook": "https://example.com/webhook",
        }
        mgr = NotificationManager(opts)
        self.assertTrue(mgr.is_enabled)

        info = MediaInfo(
            id="vid123",
            title="Notification Test Video",
            uploader="Tester",
            duration=120,
            webpage_url="https://example.com/watch?v=vid123",
            thumbnail="https://example.com/thumb.jpg",
            extractor="youtube",
        )

        with patch.object(mgr, "_post_json") as mock_post:
            mgr.notify_download_start(info)
            self.assertEqual(mock_post.call_count, 3)

        with patch.object(mgr, "_post_json") as mock_post:
            mgr.notify_download_complete(info, "/tmp/out.mp4", elapsed_seconds=5.2, total_bytes=1048576)
            self.assertEqual(mock_post.call_count, 3)

        with patch.object(mgr, "_post_json") as mock_post:
            mgr.notify_download_error("https://example.com/watch?v=vid123", "HTTP 404 Not Found")
            self.assertEqual(mock_post.call_count, 3)

    def test_watcher_daemon_cycle(self):
        mock_pydlp = MagicMock()
        daemon = WatcherDaemon(mock_pydlp, ["https://example.com/feed"], interval=1, max_cycles=2)
        with patch("time.sleep", return_value=None):
            daemon.run()
        self.assertEqual(mock_pydlp.download.call_count, 2)


if __name__ == "__main__":
    unittest.main()
