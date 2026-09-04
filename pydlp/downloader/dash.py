"""MPEG-DASH MPD manifest parser and segment downloader."""

from __future__ import annotations

import concurrent.futures
import os
import threading
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.core.utils import urljoin
from pydlp.downloader.base import BaseDownloader


class DashDownloader(BaseDownloader):
    """Downloads MPEG-DASH media streams from MPD manifests."""

    def _parse_mpd(self, mpd_url: str, xml_content: str) -> Tuple[Optional[str], List[str]]:
        """Extracts initialization and segment URLs from MPD XML."""
        # Strip default XML namespace for easier tag querying
        xml_clean = xml_content
        if "xmlns=" in xml_clean:
            import re
            xml_clean = re.sub(r'\sxmlns="[^"]+"', "", xml_clean, count=1)

        root = ET.fromstring(xml_clean)
        init_url: Optional[str] = None
        segment_urls: List[str] = []

        # Look for Representation or SegmentTemplate
        for rep in root.iter("Representation"):
            rep_id = rep.attrib.get("id", "1")
            base_url_elem = rep.find("BaseURL")
            base_url = base_url_elem.text.strip() if base_url_elem is not None and base_url_elem.text else ""

            # Check SegmentTemplate inside Representation or AdaptationSet
            seg_tmpl = rep.find("SegmentTemplate")
            if seg_tmpl is None:
                # search parent adaptation set
                for parent in root.iter("AdaptationSet"):
                    if rep in list(parent.iter("Representation")):
                        seg_tmpl = parent.find("SegmentTemplate")
                        break

            if seg_tmpl is not None:
                init_pattern = seg_tmpl.attrib.get("initialization", "")
                media_pattern = seg_tmpl.attrib.get("media", "")
                start_num = int(seg_tmpl.attrib.get("startNumber", "1"))
                timescale = int(seg_tmpl.attrib.get("timescale", "1"))

                if init_pattern:
                    init_str = init_pattern.replace("$RepresentationID$", rep_id)
                    init_url = urljoin(mpd_url, urljoin(base_url, init_str))

                # SegmentTimeline
                timeline = seg_tmpl.find("SegmentTimeline")
                if timeline is not None:
                    curr_time = 0
                    seq_num = start_num
                    for s in timeline.findall("S"):
                        t_val = s.attrib.get("t")
                        if t_val:
                            curr_time = int(t_val)
                        d = int(s.attrib.get("d", "0"))
                        r = int(s.attrib.get("r", "0"))
                        count = r + 1

                        for _ in range(count):
                            s_url = media_pattern.replace("$RepresentationID$", rep_id)
                            s_url = s_url.replace("$Time$", str(curr_time))
                            s_url = s_url.replace("$Number$", str(seq_num))
                            segment_urls.append(urljoin(mpd_url, urljoin(base_url, s_url)))
                            curr_time += d
                            seq_num += 1
                else:
                    # Generic segment range
                    for i in range(start_num, start_num + 30):
                        s_url = media_pattern.replace("$RepresentationID$", rep_id).replace("$Number$", str(i))
                        segment_urls.append(urljoin(mpd_url, urljoin(base_url, s_url)))
                break

            # Check SegmentList
            seg_list = rep.find("SegmentList")
            if seg_list is not None:
                init_elem = seg_list.find("Initialization")
                if init_elem is not None:
                    src = init_elem.attrib.get("sourceURL", "")
                    if src:
                        init_url = urljoin(mpd_url, urljoin(base_url, src))
                for seg_url_elem in seg_list.findall("SegmentURL"):
                    media_src = seg_url_elem.attrib.get("media", "")
                    if media_src:
                        segment_urls.append(urljoin(mpd_url, urljoin(base_url, media_src)))
                break

        return init_url, segment_urls

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        final_path, part_path = self._get_target_paths(filename)
        mpd_url = fmt.url

        if os.path.exists(final_path) and not self.options.get("overwrite", True):
            return True

        headers = dict(fmt.http_headers)
        resp = self.http.get(mpd_url, headers=headers)
        init_url, segment_urls = self._parse_mpd(mpd_url, resp.text())

        if not segment_urls and not init_url:
            raise DownloadError(f"Failed to parse DASH segments from MPD: {mpd_url}")

        downloaded_bytes = 0
        start_time = time.monotonic()
        total_segments = len(segment_urls) + (1 if init_url else 0)

        num_threads = min(self.options.get("concurrent_fragments", 4), 8)
        lock = threading.Lock()
        downloaded_data: Dict[int, bytes] = {}

        try:
            with open(part_path, "wb") as outfile:
                if init_url:
                    init_resp = self.http.get(init_url, headers=headers)
                    outfile.write(init_resp.content)
                    downloaded_bytes += len(init_resp.content)

                batch_size = max(num_threads * 2, 8)
                for batch_start in range(0, len(segment_urls), batch_size):
                    self.check_canceled()
                    batch_urls = segment_urls[batch_start : batch_start + batch_size]

                    def fetch_chunk(idx_url: Tuple[int, str]) -> Tuple[int, bytes]:
                        idx, s_url = idx_url
                        self.check_canceled()
                        s_resp = self.http.get(s_url, headers=headers)
                        return idx, s_resp.content

                    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                        future_to_url = {
                            executor.submit(fetch_chunk, (batch_start + j, u)): u
                            for j, u in enumerate(batch_urls)
                        }
                        for future in concurrent.futures.as_completed(future_to_url):
                            idx, data = future.result()
                            with lock:
                                downloaded_data[idx] = data

                    for j in range(len(batch_urls)):
                        seg_idx = batch_start + j
                        data = downloaded_data.pop(seg_idx, b"")
                        outfile.write(data)
                        downloaded_bytes += len(data)

                    now = time.monotonic()
                    elapsed = now - start_time
                    speed, _ = self.speed_calc.update(downloaded_bytes)
                    current_idx = min(batch_start + batch_size, len(segment_urls))
                    pct = (current_idx / total_segments) * 100.0 if total_segments > 0 else 0.0

                    self.progress_dispatcher.dispatch(
                        DownloadProgress(
                            status="downloading",
                            downloaded_bytes=downloaded_bytes,
                            speed=speed,
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
            raise DownloadError(f"DASH download failed: {e}", orig_error=e)
