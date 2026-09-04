"""Tests for downloaders and M3U8 parsing."""

import http.server
import os
import shutil
import tempfile
import threading
import time
import unittest
import urllib.request
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.downloader.hls import HlsDownloader
from pydlp.downloader.http import HttpDownloader
from pydlp.downloader.multisegment import MultiSegmentDownloader


class RangeHTTPHandler(http.server.BaseHTTPRequestHandler):
    FILE_DATA = b"ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 1000  # 36000 bytes

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", str(len(self.FILE_DATA)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()

    def do_GET(self):
        range_header = self.headers.get("Range")
        if range_header and range_header.startswith("bytes="):
            byte_range = range_header[6:].split("-")
            start = int(byte_range[0])
            end = int(byte_range[1]) if byte_range[1] else len(self.FILE_DATA) - 1
            chunk = self.FILE_DATA[start : end + 1]

            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{len(self.FILE_DATA)}")
            self.send_header("Content-Length", str(len(chunk)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(chunk)
        else:
            self.send_response(200)
            self.send_header("Content-Length", str(len(self.FILE_DATA)))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(self.FILE_DATA)

    def log_message(self, format, *args):
        pass


class TestDownloader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_address = ("127.0.0.1", 19999)
        cls.httpd = http.server.ThreadingHTTPServer(cls.server_address, RangeHTTPHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.http_client = HttpClient()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_http_downloader(self):
        out_file = os.path.join(self.test_dir, "test_file.bin")
        downloader = HttpDownloader(self.http_client, {"quiet": True})
        fmt = MediaFormat(format_id="1", url="http://127.0.0.1:19999/test.bin", ext="bin")
        info = MediaInfo(id="test", title="Test", extractor="test", extractor_key="Test")

        success = downloader.download(out_file, info, fmt)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_file))
        self.assertEqual(os.path.getsize(out_file), len(RangeHTTPHandler.FILE_DATA))

    def test_hls_m3u8_parser(self):
        manifest = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:9.009,
segment1.ts
#EXTINF:9.009,
segment2.ts
#EXT-X-ENDLIST
"""
        downloader = HlsDownloader(self.http_client)
        segments, init_seg = downloader._parse_playlist("http://example.com/hls/master.m3u8", manifest)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].url, "http://example.com/hls/segment1.ts")
        self.assertEqual(segments[1].url, "http://example.com/hls/segment2.ts")


if __name__ == "__main__":
    unittest.main()
