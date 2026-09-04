"""Tests for HTTP client, cookies, and rate limiting."""

import unittest
from pydlp.core.cookies import NetscapeCookieJar, build_cookie_header, parse_cookie_header
from pydlp.core.http import HttpClient, RateLimiter
from pydlp.core.utils import format_bytes, format_seconds, format_speed, parse_duration, parse_filesize


class TestHttpAndUtils(unittest.TestCase):
    def test_cookie_parsing(self):
        cookie_header = "session_id=abc12345; user=john_doe; theme=dark"
        cookies = parse_cookie_header(cookie_header)
        self.assertEqual(cookies["session_id"], "abc12345")
        self.assertEqual(cookies["user"], "john_doe")
        self.assertEqual(cookies["theme"], "dark")
        rebuilt = build_cookie_header(cookies)
        self.assertIn("session_id=abc12345", rebuilt)

    def test_netscape_cookie_loader(self):
        jar = NetscapeCookieJar()
        netscape_text = """# Netscape HTTP Cookie File
.youtube.com\tTRUE\t/\tTRUE\t1900000000\tPREF\tf1=50000000
.example.com\tTRUE\t/\tFALSE\t1900000000\tsid\txyz123
"""
        jar.load_from_string(netscape_text)
        cookie_names = [c.name for c in jar]
        self.assertIn("PREF", cookie_names)
        self.assertIn("sid", cookie_names)

    def test_utils_format_bytes(self):
        self.assertEqual(format_bytes(1024), "1.00KiB")
        self.assertEqual(format_bytes(1024 * 1024 * 5), "5.00MiB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 2.5), "2.50GiB")
        self.assertEqual(format_bytes(None), "N/A")

    def test_utils_format_speed(self):
        self.assertEqual(format_speed(1024 * 1024 * 2), "2.00MiB/s")

    def test_utils_format_seconds(self):
        self.assertEqual(format_seconds(65), "01:05")
        self.assertEqual(format_seconds(3665), "01:01:05")

    def test_utils_parse_duration(self):
        self.assertEqual(parse_duration("01:30"), 90.0)
        self.assertEqual(parse_duration("01:02:03"), 3723.0)
        self.assertEqual(parse_duration("PT1H2M3S"), 3723.0)
        self.assertEqual(parse_duration("45"), 45.0)

    def test_utils_parse_filesize(self):
        self.assertEqual(parse_filesize("10MB"), 10000000)
        self.assertEqual(parse_filesize("10MiB"), 10485760)
        self.assertEqual(parse_filesize("1GiB"), 1073741824)

    def test_http_get_raw_attribute(self):
        client = HttpClient()
        self.assertTrue(hasattr(client, "get_raw"))
        self.assertTrue(callable(client.get_raw))

    def test_http_request_stream_arg_and_response_status(self):
        client = HttpClient()
        from unittest.mock import MagicMock, patch
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.headers = {"content-type": "video/mp4"}
        mock_resp.geturl.return_value = "https://example.com/stream.mp4"
        mock_resp.read.return_value = b"video data"

        with patch.object(client._opener, "open", return_value=mock_resp):
            resp = client.request("GET", "https://example.com/stream.mp4", stream=True, custom_flag="test")
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.read(5), b"video data")


if __name__ == "__main__":
    unittest.main()
