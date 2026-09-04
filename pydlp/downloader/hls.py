"""HLS (HTTP Live Streaming) M3U8 parser and segment downloader."""

from __future__ import annotations

import concurrent.futures
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.core.utils import parse_m3u8_attributes, urljoin
from pydlp.downloader.base import BaseDownloader


class HlsSegment:
    def __init__(
        self,
        index: int,
        url: str,
        duration: float = 0.0,
        key_url: Optional[str] = None,
        key_iv: Optional[bytes] = None,
        byte_range: Optional[Tuple[int, Optional[int]]] = None,
        is_init_segment: bool = False,
    ):
        self.index = index
        self.url = url
        self.duration = duration
        self.key_url = key_url
        self.key_iv = key_iv
        self.byte_range = byte_range
        self.is_init_segment = is_init_segment


class HlsDownloader(BaseDownloader):
    """Downloads HLS/M3U8 media streams segment by segment."""

    def _parse_playlist(self, manifest_url: str, manifest_text: str) -> Tuple[List[HlsSegment], Optional[HlsSegment]]:
        """Parses M3U8 media playlist text into segments."""
        lines = [line.strip() for line in manifest_text.splitlines() if line.strip()]
        segments: List[HlsSegment] = []
        init_segment: Optional[HlsSegment] = None

        current_key_url: Optional[str] = None
        current_iv: Optional[bytes] = None
        current_duration: float = 0.0
        current_byte_range: Optional[Tuple[int, Optional[int]]] = None
        seg_idx = 0

        for line in lines:
            if line.startswith("#EXT-X-KEY:"):
                attrs = parse_m3u8_attributes(line[11:])
                method = attrs.get("METHOD", "NONE")
                if method == "AES-128":
                    uri = attrs.get("URI", "")
                    current_key_url = urljoin(manifest_url, uri) if uri else None
                    iv_str = attrs.get("IV", "")
                    if iv_str:
                        clean_iv = iv_str.replace("0x", "")
                        current_iv = bytes.fromhex(clean_iv)
                    else:
                        current_iv = None
                else:
                    current_key_url = None
                    current_iv = None

            elif line.startswith("#EXT-X-MAP:"):
                attrs = parse_m3u8_attributes(line[11:])
                uri = attrs.get("URI", "")
                if uri:
                    init_url = urljoin(manifest_url, uri)
                    init_segment = HlsSegment(index=-1, url=init_url, is_init_segment=True)

            elif line.startswith("#EXTINF:"):
                dur_match = re.match(r"#EXTINF:([0-9.]+)", line)
                if dur_match:
                    current_duration = float(dur_match.group(1))

            elif line.startswith("#EXT-X-BYTERANGE:"):
                range_str = line[17:]
                if "@" in range_str:
                    length, offset = range_str.split("@", 1)
                    start = int(offset)
                    end = start + int(length) - 1
                    current_byte_range = (start, end)
                else:
                    length = int(range_str)
                    current_byte_range = (0, length - 1)

            elif not line.startswith("#"):
                seg_url = urljoin(manifest_url, line)
                segments.append(
                    HlsSegment(
                        index=seg_idx,
                        url=seg_url,
                        duration=current_duration,
                        key_url=current_key_url,
                        key_iv=current_iv,
                        byte_range=current_byte_range,
                    )
                )
                seg_idx += 1
                current_byte_range = None

        return segments, init_segment

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        final_path, part_path = self._get_target_paths(filename)
        m3u8_url = fmt.url

        if os.path.exists(final_path) and not self.options.get("overwrite", True):
            return True

        headers = dict(fmt.http_headers)

        # Download playlist manifest
        resp = self.http.get(m3u8_url, headers=headers)
        playlist_text = resp.text()

        # If it is a master playlist containing variant streams, pick the sub stream
        if "#EXT-X-STREAM-INF:" in playlist_text:
            lines = playlist_text.splitlines()
            sub_url = None
            for i, line in enumerate(lines):
                if line.startswith("#EXT-X-STREAM-INF:") and i + 1 < len(lines):
                    sub_url = lines[i + 1].strip()
                    break
            if sub_url:
                m3u8_url = urljoin(m3u8_url, sub_url)
                resp = self.http.get(m3u8_url, headers=headers)
                playlist_text = resp.text()

        segments, init_segment = self._parse_playlist(m3u8_url, playlist_text)
        if not segments:
            raise DownloadError(f"No media segments found in M3U8 manifest: {m3u8_url}")

        total_segments = len(segments)
        downloaded_bytes = 0
        start_time = time.monotonic()
        last_progress_time = 0.0

        num_threads = min(self.options.get("concurrent_fragments", 4), 8)
        lock = threading.Lock()
        downloaded_segments_data: Dict[int, bytes] = {}

        try:
            with open(part_path, "wb") as outfile:
                # If there is an init segment (fMP4), fetch and write first
                if init_segment:
                    init_resp = self.http.get(init_segment.url, headers=headers)
                    outfile.write(init_resp.content)
                    downloaded_bytes += len(init_resp.content)

                # Download segments in windows/batches to conserve RAM while allowing high concurrency
                batch_size = max(num_threads * 2, 8)
                for batch_start in range(0, total_segments, batch_size):
                    self.check_canceled()
                    batch_segs = segments[batch_start : batch_start + batch_size]

                    def fetch_seg(seg: HlsSegment) -> Tuple[int, bytes]:
                        self.check_canceled()
                        s_resp = self.http.get(seg.url, headers=headers, byte_range=seg.byte_range)
                        data = s_resp.content
                        return seg.index, data

                    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                        future_to_seg = {executor.submit(fetch_seg, s): s for s in batch_segs}
                        for future in concurrent.futures.as_completed(future_to_seg):
                            seg_idx, data = future.result()
                            with lock:
                                downloaded_segments_data[seg_idx] = data

                    # Write finished segments in sequential index order
                    for seg in batch_segs:
                        seg_data = downloaded_segments_data.pop(seg.index, b"")
                        outfile.write(seg_data)
                        downloaded_bytes += len(seg_data)

                    now = time.monotonic()
                    elapsed = now - start_time
                    speed, _ = self.speed_calc.update(downloaded_bytes)
                    current_idx = min(batch_start + batch_size, total_segments)
                    pct = (current_idx / total_segments) * 100.0

                    self.progress_dispatcher.dispatch(
                        DownloadProgress(
                            status="downloading",
                            downloaded_bytes=downloaded_bytes,
                            total_bytes=None,
                            total_bytes_estimate=int(downloaded_bytes / (pct / 100.0)) if pct > 0 else None,
                            speed=speed,
                            eta=None,
                            elapsed=elapsed,
                            percentage=pct,
                            filename=final_path,
                            tmp_filename=part_path,
                            fragment_index=current_idx,
                            fragment_count=total_segments,
                            info_dict=info_dict.to_dict() if info_dict else None,
                        )
                    )

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
            raise
        except Exception as e:
            raise DownloadError(f"HLS download failed: {e}", orig_error=e)
