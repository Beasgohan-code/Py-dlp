"""Live HLS continuous stream recorder."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Set

from pydlp.core.exceptions import CancelRequested, DownloadError
from pydlp.core.http import HttpClient
from pydlp.core.types import DownloadProgress, MediaFormat, MediaInfo
from pydlp.core.utils import urljoin
from pydlp.downloader.base import BaseDownloader


class HLSLiveDownloader(BaseDownloader):
    """Continuous Live Stream HLS recorder tracking sliding-window playlists."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(http_client, options)
        self.live_duration = float(self.options.get("live_record_duration") or 0)  # 0 = until stream ends or cancel

    def download(self, filename: str, info_dict: MediaInfo, fmt: MediaFormat) -> bool:
        if not fmt.url:
            raise DownloadError("Live format has no manifest URL")

        final_path, part_path = self._get_target_paths(filename)
        headers = dict(fmt.http_headers or {})

        downloaded_bytes = 0
        seen_segments: Set[str] = set()
        start_time = time.time()
        last_dispatch = start_time

        with open(part_path, "wb") as out_file:
            while True:
                self.check_canceled()

                # Check duration limit
                if self.live_duration > 0 and (time.time() - start_time) >= self.live_duration:
                    break

                try:
                    resp = self.http.get(fmt.url, headers=headers)
                    playlist_text = resp.text()
                except Exception as e:
                    time.sleep(2.0)
                    continue

                lines = [l.strip() for l in playlist_text.splitlines() if l.strip()]
                target_duration = 4.0
                is_endlist = False

                for line in lines:
                    if line.startswith("#EXT-X-TARGETDURATION:"):
                        try:
                            target_duration = float(line.split(":")[1])
                        except Exception:
                            pass
                    elif line.startswith("#EXT-X-ENDLIST"):
                        is_endlist = True

                new_segments: List[str] = []
                for line in lines:
                    if not line.startswith("#"):
                        seg_url = urljoin(fmt.url, line)
                        if seg_url not in seen_segments:
                            seen_segments.add(seg_url)
                            new_segments.append(seg_url)

                for seg_url in new_segments:
                    self.check_canceled()
                    try:
                        seg_resp = self.http.get(seg_url, headers=headers)
                        data = seg_resp.content()
                        if data:
                            out_file.write(data)
                            downloaded_bytes += len(data)
                            self.speed_calc.update(downloaded_bytes)
                    except Exception:
                        continue

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

                if is_endlist:
                    break

                time.sleep(max(target_duration / 2.0, 1.0))

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
