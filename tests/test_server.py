"""Tests for Py-dlp Web Server and REST API."""

import http.server
import json
import threading
import time
import unittest
import urllib.request
from pydlp.server.app import PyDLPRequestHandler
from pydlp.server.handlers import DownloadTaskManager


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_address = ("127.0.0.1", 18888)
        cls.httpd = http.server.ThreadingHTTPServer(cls.server_address, PyDLPRequestHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def test_status_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:18888/api/status")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertEqual(data["name"], "Py-dlp")
        self.assertEqual(data["status"], "online")
        self.assertGreaterEqual(data["extractors_count"], 15)

    def test_extractors_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:18888/api/extractors")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("extractors", data)
        names = [ie["name"] for ie in data["extractors"]]
        self.assertIn("youtube", names)
        self.assertIn("tiktok", names)
        self.assertIn("twitter", names)

    def test_tasks_endpoint(self):
        req = urllib.request.urlopen("http://127.0.0.1:18888/api/tasks")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("tasks", data)

    def test_task_manager(self):
        tm = DownloadTaskManager(max_concurrent=2)
        task_id = tm.submit_task("https://example.com/test.mp4", {"simulate": True})
        self.assertIsNotNone(task_id)
        task = tm.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["url"], "https://example.com/test.mp4")


if __name__ == "__main__":
    unittest.main()
