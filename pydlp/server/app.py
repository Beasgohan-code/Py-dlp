"""Built-in HTTP server and REST API for Py-dlp Web Dashboard."""

from __future__ import annotations

import http.server
import json
import os
import urllib.parse
from typing import Any, Dict, Optional

from pydlp.core.types import MediaInfo
from pydlp.extractor import list_extractors
from pydlp.pydlp import PyDLP
from pydlp.server.handlers import GLOBAL_TASK_MANAGER
from pydlp.version import __version__


class PyDLPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Handles REST API requests and serves embedded static dashboard files."""

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")

    def _send_json(self, data: Any, status_code: int = 200) -> None:
        payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # 1. API: /api/status
        if path == "/api/status":
            self._send_json(
                {
                    "name": "Py-dlp",
                    "version": __version__,
                    "status": "online",
                    "extractors_count": len(list_extractors()),
                }
            )
            return

        # 2. API: /api/extractors
        elif path == "/api/extractors":
            extractors_list = [
                {
                    "name": ie.IE_NAME,
                    "desc": ie.IE_DESC or ie.IE_NAME,
                    "key": ie.ie_key(),
                }
                for ie in list_extractors()
            ]
            self._send_json({"extractors": extractors_list})
            return

        # 3. API: /api/tasks
        elif path == "/api/tasks":
            tasks = GLOBAL_TASK_MANAGER.get_all_tasks()
            self._send_json({"tasks": tasks})
            return

        # 4. API: /api/tasks/<id>
        elif path.startswith("/api/tasks/"):
            task_id = path[len("/api/tasks/"):]
            task = GLOBAL_TASK_MANAGER.get_task(task_id)
            if task:
                self._send_json(task)
            else:
                self._send_json({"error": "Task not found"}, status_code=404)
            return

        # 5. Static Web UI files
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        req_file = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
        file_path = os.path.join(static_dir, req_file)

        if os.path.isfile(file_path):
            content_type = "text/html; charset=utf-8"
            if file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            elif file_path.endswith(".json"):
                content_type = "application/json"
            elif file_path.endswith(".png"):
                content_type = "image/png"
            elif file_path.endswith(".svg"):
                content_type = "image/svg+xml"

            with open(file_path, "rb") as f:
                body = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
        else:
            self._send_json({"error": "Not Found"}, status_code=404)

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            req_data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON request payload"}, status_code=400)
            return

        # 1. API: /api/extract
        if path == "/api/extract":
            url = req_data.get("url", "").strip()
            if not url:
                self._send_json({"error": "Missing 'url' parameter", "success": False}, status_code=400)
                return

            client = PyDLP({"simulate": True, "quiet": True})
            try:
                info = client.extract_info(url, download=False)
                if info:
                    self._send_json({"success": True, "data": info.to_dict()})
                else:
                    self._send_json({"success": False, "error": "Could not extract media info"})
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status_code=500)
            return

        # 2. API: /api/download
        elif path == "/api/download":
            url = req_data.get("url", "").strip()
            if not url:
                self._send_json({"error": "Missing 'url' parameter", "success": False}, status_code=400)
                return

            options = {
                "format": req_data.get("format", "bestvideo+bestaudio/best"),
                "extract_audio": bool(req_data.get("extract_audio", False)),
                "audio_format": req_data.get("audio_format", "mp3"),
                "paths": req_data.get("paths"),
            }
            task_id = GLOBAL_TASK_MANAGER.submit_task(url, options)
            self._send_json({"success": True, "task_id": task_id})
            return

        else:
            self._send_json({"error": "Not Found"}, status_code=404)

    def log_message(self, format: str, *args: Any) -> None:
        # Clean log silencing
        pass


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Starts the built-in Py-dlp Web Server."""
    server_address = (host, port)
    httpd = http.server.ThreadingHTTPServer(server_address, PyDLPRequestHandler)
    print(f"[server] Py-dlp Web UI running at http://{host}:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] Shutting down...")
        httpd.server_close()
