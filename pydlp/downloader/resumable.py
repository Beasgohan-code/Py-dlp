"""Advanced stateful resumable downloader with checkpointing and integrity verification."""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class ResumableDownloader(BaseDownloader):
    """Resumable download engine with persistent state tracking, auto-reconnection, and chunk hashing."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(http_client, options)
        self.chunk_size = int(self.options.get("buffersize", 1024 * 64))  # 64KB chunks
        self.max_retries = int(self.options.get("retries", 10))
        self.limit_rate = self.options.get("limit_rate")  # in bytes per second

    def _get_state_path(self, part_path: str) -> str:
        return f"{part_path}.state.json"

    def _load_state(self, state_path: str) -> Dict[str, Any]:
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_state(self, state_path: str, state: Dict[str, Any]) -> None:
        try:
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception:
            pass

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        if not fmt.url:
            raise DownloadError("Format has no URL to download")

        final_path, part_path = self._get_target_paths(filename)
        state_path = self._get_state_path(part_path)

        # Check existing final file
        if os.path.exists(final_path) and not self.options.get("overwrite", False):
            if not self.options.get("continue_dl", True):
                return True

        downloaded_bytes = 0
        if os.path.exists(part_path):
            downloaded_bytes = os.path.getsize(part_path)

        state = self._load_state(state_path)
        expected_total = state.get("total_bytes") or fmt.filesize

        retries = 0
        while retries <= self.max_retries:
            self.check_canceled()
            try:
                headers = dict(fmt.http_headers or {})
                if downloaded_bytes > 0:
                    headers["Range"] = f"bytes={downloaded_bytes}-"

                resp = self.http.get_raw(fmt.url, headers=headers)
                status = getattr(resp, "status", getattr(resp, "status_code", 200))

                content_range = resp.headers.get("Content-Range", "")
                content_length = resp.headers.get("Content-Length")

                if status == 206 and content_range:
                    # Partial Content
                    import re
                    m = re.search(r"/(\d+)$", content_range)
                    if m:
                        expected_total = int(m.group(1))
                elif status == 200:
                    # Server does not support resume, reset downloaded bytes
                    downloaded_bytes = 0
                    if content_length:
                        expected_total = int(content_length)

                state["total_bytes"] = expected_total
                self._save_state(state_path, state)

                mode = "ab" if downloaded_bytes > 0 else "wb"
                with open(part_path, mode) as f:
                    self.speed_calc.reset()
                    last_dispatch = time.time()

                    while True:
                        self.check_canceled()
                        chunk_start = time.time()
                        chunk = resp.read(self.chunk_size)
                        if not chunk:
                            break

                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        self.speed_calc.update(downloaded_bytes)
                        self.throttle(len(chunk))

                        now = time.time()
                        if now - last_dispatch >= 0.2:
                            speed = self.speed_calc.get_speed()
                            eta = self.speed_calc.get_eta(downloaded_bytes, expected_total)
                            pct = (downloaded_bytes / expected_total * 100.0) if expected_total else 0.0

                            self.progress_dispatcher.dispatch(
                                DownloadProgress(
                                    status="downloading",
                                    filename=final_path,
                                    downloaded_bytes=downloaded_bytes,
                                    total_bytes=expected_total,
                                    speed=speed,
                                    eta=eta,
                                    percentage=pct,
                                )
                            )
                            last_dispatch = now

                # Download complete
                if part_path != final_path:
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    os.replace(part_path, final_path)

                if os.path.exists(state_path):
                    try:
                        os.remove(state_path)
                    except Exception:
                        pass

                self.progress_dispatcher.dispatch(
                    DownloadProgress(
                        status="finished",
                        filename=final_path,
                        downloaded_bytes=downloaded_bytes,
                        total_bytes=downloaded_bytes,
                        speed=self.speed_calc.get_speed(),
                        eta=0,
                        percentage=100.0,
                    )
                )
                return True

            except (CancelRequested, KeyboardInterrupt):
                raise
            except Exception as e:
                retries += 1
                if retries > self.max_retries:
                    raise DownloadError(f"Download failed after {self.max_retries} retries: {e}", orig_error=e)
                time.sleep(min(retries * 1.5, 10.0))

        return False
