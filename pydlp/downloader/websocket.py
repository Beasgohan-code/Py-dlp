"""WebSocket & Live Stream chunked media capture engine."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class WebSocketDownloader(BaseDownloader):
    """Downloads media from raw chunked streaming endpoints and WebSocket media sockets."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(http_client, options)
        self.chunk_size = 1024 * 32

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        if not fmt.url:
            raise DownloadError("Stream format has no URL")

        final_path, part_path = self._get_target_paths(filename)
        headers = dict(fmt.http_headers or {})

        downloaded_bytes = 0
        last_dispatch = time.time()

        try:
            resp = self.http.get_raw(fmt.url, headers=headers)
            with open(part_path, "wb") as f:
                while True:
                    self.check_canceled()
                    chunk = resp.read(self.chunk_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded_bytes += len(chunk)
                    self.speed_calc.update(downloaded_bytes)

                    now = time.time()
                    if now - last_dispatch >= 0.5:
                        speed = self.speed_calc.get_speed()
                        self.progress_dispatcher.dispatch(
                            DownloadProgress(
                                status="downloading",
                                filename=final_path,
                                downloaded_bytes=downloaded_bytes,
                                speed=speed,
                                eta=0,
                                percentage=0.0,
                            )
                        )
                        last_dispatch = now

            if part_path != final_path:
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.replace(part_path, final_path)

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

        except Exception as e:
            raise DownloadError(f"Stream capture error: {e}", orig_error=e)
