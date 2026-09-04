"""Request handlers and task manager for the Py-dlp Web Server and REST API."""

from __future__ import annotations

import concurrent.futures
import json
import os
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from pydlp.core.types import DownloadProgress, MediaInfo
from pydlp.extractor import list_extractors
from pydlp.pydlp import PyDLP


class DownloadTaskManager:
    """Manages asynchronous background download jobs."""

    def __init__(self, max_concurrent: int = 4):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent)
        self._lock = threading.Lock()

    def submit_task(self, url: str, options: Optional[Dict[str, Any]] = None) -> str:
        task_id = str(uuid.uuid4())[:8]
        task_data = {
            "id": task_id,
            "url": url,
            "title": url,
            "status": "queued",
            "progress": None,
            "error": None,
            "created_at": time.time(),
            "completed_at": None,
        }
        with self._lock:
            self.tasks[task_id] = task_data

        def _worker():
            with self._lock:
                self.tasks[task_id]["status"] = "downloading"

            def _progress_hook(p: DownloadProgress):
                with self._lock:
                    self.tasks[task_id]["progress"] = p.to_dict()
                    if p.info_dict and p.info_dict.get("title"):
                        self.tasks[task_id]["title"] = p.info_dict["title"]

            pydlp_opts = dict(options or {})
            pydlp_opts["quiet"] = True
            client = PyDLP(pydlp_opts)
            client.add_progress_hook(_progress_hook)

            try:
                info = client.extract_info(url, download=True)
                with self._lock:
                    self.tasks[task_id]["status"] = "finished"
                    self.tasks[task_id]["completed_at"] = time.time()
                    if info:
                        self.tasks[task_id]["title"] = info.title
            except Exception as e:
                with self._lock:
                    self.tasks[task_id]["status"] = "error"
                    self.tasks[task_id]["error"] = str(e)
                    self.tasks[task_id]["completed_at"] = time.time()

        self._executor.submit(_worker)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return sorted(list(self.tasks.values()), key=lambda x: x["created_at"], reverse=True)


GLOBAL_TASK_MANAGER = DownloadTaskManager()
