"""HTTP/HTTPS stream downloader with range resumption support."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class HttpDownloader(BaseDownloader):
    """Downloads files over HTTP/HTTPS with support for pause, resume, and rate limiting."""

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        final_path, part_path = self._get_target_paths(filename)
        url = fmt.url

        # Check if already fully downloaded
        if os.path.exists(final_path) and not self.options.get("overwrite", True):
            return True

        downloaded_bytes = 0
        resume_byte = 0
        file_mode = "wb"

        # Check for partial download resumption
        if os.path.exists(part_path) and self.options.get("continue_dl", True):
            existing_size = os.path.getsize(part_path)
            if existing_size > 0:
                resume_byte = existing_size
                downloaded_bytes = existing_size
                file_mode = "ab"

        headers = dict(fmt.http_headers)
        byte_range = (resume_byte, None) if resume_byte > 0 else None

        start_time = time.monotonic()
        last_progress_time = 0.0

        try:
            # Initial HEAD or GET to obtain Content-Length if possible
            total_bytes = fmt.filesize
            if not total_bytes:
                try:
                    head_resp = self.http.head(url, headers=headers, timeout=10.0)
                    cl = head_resp.headers.get("content-length")
                    if cl and cl.isdigit():
                        total_bytes = int(cl) + (resume_byte if resume_byte > 0 else 0)
                except Exception:
                    pass

            chunk_size = self.options.get("buffersize", 64 * 1024)

            with open(part_path, file_mode) as f:
                stream = self.http.stream(
                    url=url,
                    chunk_size=chunk_size,
                    headers=headers,
                    byte_range=byte_range,
                )

                for chunk in stream:
                    self.check_canceled()
                    f.write(chunk)
                    downloaded_bytes += len(chunk)
                    self.throttle(len(chunk))

                    now = time.monotonic()
                    if now - last_progress_time >= 0.1:
                        last_progress_time = now
                        elapsed = now - start_time
                        speed, _ = self.speed_calc.update(downloaded_bytes)

                        eta = None
                        if speed and speed > 0 and total_bytes and total_bytes > downloaded_bytes:
                            eta = (total_bytes - downloaded_bytes) / speed

                        pct = (downloaded_bytes / total_bytes * 100.0) if total_bytes and total_bytes > 0 else 0.0

                        self.progress_dispatcher.dispatch(
                            DownloadProgress(
                                status="downloading",
                                downloaded_bytes=downloaded_bytes,
                                total_bytes=total_bytes,
                                speed=speed,
                                eta=eta,
                                elapsed=elapsed,
                                percentage=pct,
                                filename=final_path,
                                tmp_filename=part_path,
                                info_dict=info_dict.to_dict() if info_dict else None,
                            )
                        )

            # Successfully completed
            if part_path != final_path:
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(part_path, final_path)

            elapsed = time.monotonic() - start_time
            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="finished",
                    downloaded_bytes=downloaded_bytes,
                    total_bytes=downloaded_bytes,
                    speed=downloaded_bytes / elapsed if elapsed > 0 else None,
                    eta=0.0,
                    elapsed=elapsed,
                    percentage=100.0,
                    filename=final_path,
                    info_dict=info_dict.to_dict() if info_dict else None,
                )
            )
            return True

        except CancelRequested:
            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="cancelled",
                    downloaded_bytes=downloaded_bytes,
                    filename=final_path,
                    error="Download cancelled by user",
                )
            )
            raise
        except Exception as e:
            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="error",
                    downloaded_bytes=downloaded_bytes,
                    filename=final_path,
                    error=str(e),
                )
            )
            raise DownloadError(f"HTTP download failed: {e}", orig_error=e)
