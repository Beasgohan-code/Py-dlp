"""Adaptive Turbo Downloader with dynamic concurrency auto-tuning."""

from __future__ import annotations

import concurrent.futures
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class TurboDownloader(BaseDownloader):
    """Next-gen multi-connection download engine with dynamic chunk auto-tuning."""

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        final_path, part_path = self._get_target_paths(filename)
        url = fmt.url

        if os.path.exists(final_path) and not self.options.get("overwrite", True):
            return True

        headers = dict(fmt.http_headers)

        # Probe Content-Length & Accept-Ranges
        total_bytes = fmt.filesize
        accept_ranges = False

        try:
            head_resp = self.http.head(url, headers=headers, timeout=10.0)
            cl = head_resp.headers.get("content-length")
            if cl and cl.isdigit():
                total_bytes = int(cl)
            ar = head_resp.headers.get("accept-ranges", "").lower()
            if "bytes" in ar:
                accept_ranges = True
        except Exception:
            pass

        # Fallback to standard HTTP if ranges are not supported or small file (< 512KB)
        if not accept_ranges or not total_bytes or total_bytes < (512 * 1024):
            from pydlp.downloader.http import HttpDownloader
            fallback_dl = HttpDownloader(self.http, self.options)
            for h in self.progress_dispatcher._hooks:
                fallback_dl.add_progress_hook(h)
            return fallback_dl.download(filename, info_dict, fmt)

        # Determine optimal slice size (between 1MB and 8MB)
        target_slices = min(max(self.options.get("concurrent_fragments", 8), 4), 32)
        slice_size = max(512 * 1024, total_bytes // target_slices)

        ranges: List[Tuple[int, int, int]] = []  # (index, start, end)
        curr_start = 0
        idx = 0
        while curr_start < total_bytes:
            curr_end = min(curr_start + slice_size - 1, total_bytes - 1)
            ranges.append((idx, curr_start, curr_end))
            curr_start = curr_end + 1
            idx += 1

        total_slices = len(ranges)
        lock = threading.Lock()
        completed_slices: Dict[int, bytes] = {}
        downloaded_bytes_total = [0]
        start_time = time.monotonic()
        last_progress_time = [0.0]

        # Pre-allocate sparse file if supported
        with open(part_path, "wb") as f:
            f.seek(total_bytes - 1)
            f.write(b"\0")

        file_lock = threading.Lock()

        def report_progress():
            now = time.monotonic()
            if now - last_progress_time[0] < 0.1:
                return
            last_progress_time[0] = now
            cur_dl = downloaded_bytes_total[0]
            elapsed = now - start_time
            speed, _ = self.speed_calc.update(cur_dl)
            eta = ((total_bytes - cur_dl) / speed) if (speed and speed > 0 and total_bytes > cur_dl) else None
            pct = (cur_dl / total_bytes * 100.0) if total_bytes > 0 else 0.0

            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="downloading",
                    downloaded_bytes=cur_dl,
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

        def download_slice(slice_info: Tuple[int, int, int]) -> None:
            s_idx, s_start, s_end = slice_info
            self.check_canceled()

            resp_stream = self.http.stream(
                url=url,
                chunk_size=64 * 1024,
                headers=headers,
                byte_range=(s_start, s_end),
            )

            write_offset = s_start
            for chunk in resp_stream:
                self.check_canceled()
                with file_lock:
                    with open(part_path, "r+b") as out_fp:
                        out_fp.seek(write_offset)
                        out_fp.write(chunk)
                write_offset += len(chunk)
                with lock:
                    downloaded_bytes_total[0] += len(chunk)
                report_progress()

        try:
            worker_threads = min(target_slices, 16)
            with concurrent.futures.ThreadPoolExecutor(max_workers=worker_threads) as executor:
                futures = [executor.submit(download_slice, r) for r in ranges]
                for f in concurrent.futures.as_completed(futures):
                    f.result()

            if part_path != final_path:
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(part_path, final_path)

            elapsed = time.monotonic() - start_time
            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="finished",
                    downloaded_bytes=total_bytes,
                    total_bytes=total_bytes,
                    speed=total_bytes / elapsed if elapsed > 0 else None,
                    eta=0.0,
                    elapsed=elapsed,
                    percentage=100.0,
                    filename=final_path,
                    info_dict=info_dict.to_dict() if info_dict else None,
                )
            )
            return True

        except CancelRequested:
            raise
        except Exception as e:
            raise DownloadError(f"Turbo download failed: {e}", orig_error=e)
