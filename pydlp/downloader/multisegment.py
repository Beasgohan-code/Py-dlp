"""Multi-threaded segmented downloader for accelerated media downloads."""

from __future__ import annotations

import concurrent.futures
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.downloader.base import BaseDownloader


class MultiSegmentDownloader(BaseDownloader):
    """Downloads files concurrently by splitting byte ranges across worker threads."""

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        final_path, part_path = self._get_target_paths(filename)
        url = fmt.url

        if os.path.exists(final_path) and not self.options.get("overwrite", True):
            return True

        num_threads = self.options.get("concurrent_fragments", 4)
        headers = dict(fmt.http_headers)

        # Probe server capabilities and file size
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

        # If server does not support ranges or total size is too small / unknown, fallback to single stream
        if not accept_ranges or not total_bytes or total_bytes < (1024 * 1024) or num_threads <= 1:
            from pydlp.downloader.http import HttpDownloader
            single_dl = HttpDownloader(self.http, self.options)
            for h in self.progress_dispatcher._hooks:
                single_dl.add_progress_hook(h)
            return single_dl.download(filename, info_dict, fmt)

        # Calculate chunk ranges
        chunk_size = total_bytes // num_threads
        segments: List[Tuple[int, int, int, str]] = []  # (seg_idx, start, end, seg_file)
        for i in range(num_threads):
            start = i * chunk_size
            end = (start + chunk_size - 1) if i < num_threads - 1 else (total_bytes - 1)
            seg_file = f"{part_path}.seg{i}"
            segments.append((i, start, end, seg_file))

        lock = threading.Lock()
        downloaded_per_seg = [0] * num_threads
        start_time = time.monotonic()
        last_progress_time = [0.0]

        def report_progress():
            now = time.monotonic()
            if now - last_progress_time[0] < 0.1:
                return
            last_progress_time[0] = now
            with lock:
                current_downloaded = sum(downloaded_per_seg)
            elapsed = now - start_time
            speed, _ = self.speed_calc.update(current_downloaded)
            eta = ((total_bytes - current_downloaded) / speed) if (speed and speed > 0 and total_bytes > current_downloaded) else None
            pct = (current_downloaded / total_bytes * 100.0) if total_bytes > 0 else 0.0

            self.progress_dispatcher.dispatch(
                DownloadProgress(
                    status="downloading",
                    downloaded_bytes=current_downloaded,
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

        def download_segment(seg_info: Tuple[int, int, int, str]) -> None:
            seg_idx, start_byte, end_byte, seg_path = seg_info
            current_start = start_byte

            # Check if segment partially exists
            if os.path.exists(seg_path):
                existing_seg_size = os.path.getsize(seg_path)
                if existing_seg_size >= (end_byte - start_byte + 1):
                    with lock:
                        downloaded_per_seg[seg_idx] = existing_seg_size
                    return
                current_start += existing_seg_size
                with lock:
                    downloaded_per_seg[seg_idx] = existing_seg_size

            mode = "ab" if current_start > start_byte else "wb"
            with open(seg_path, mode) as sf:
                stream = self.http.stream(
                    url=url,
                    chunk_size=32 * 1024,
                    headers=headers,
                    byte_range=(current_start, end_byte),
                )
                for chunk in stream:
                    self.check_canceled()
                    sf.write(chunk)
                    with lock:
                        downloaded_per_seg[seg_idx] += len(chunk)
                    report_progress()

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(download_segment, seg) for seg in segments]
                for f in concurrent.futures.as_completed(futures):
                    f.result()

            # Stitch segment files together into part_path
            with open(part_path, "wb") as outfile:
                for _, _, _, seg_path in segments:
                    if os.path.exists(seg_path):
                        with open(seg_path, "rb") as sf:
                            while True:
                                data = sf.read(512 * 1024)
                                if not data:
                                    break
                                outfile.write(data)
                        try:
                            os.remove(seg_path)
                        except OSError:
                            pass

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
            for _, _, _, seg_path in segments:
                if os.path.exists(seg_path):
                    try:
                        os.remove(seg_path)
                    except OSError:
                        pass
            raise
        except Exception as e:
            raise DownloadError(f"Multi-segment download failed: {e}", orig_error=e)
