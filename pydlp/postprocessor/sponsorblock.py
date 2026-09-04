"""SponsorBlock post-processor for cutting or marking sponsored intervals."""

from __future__ import annotations

import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.exceptions import PostProcessingError
from pydlp.core.http import HttpClient
from pydlp.core.sponsorblock import SponsorBlockAPI, SponsorSegment
from pydlp.core.types import MediaChapter, MediaInfo
from pydlp.postprocessor.base import BasePostProcessor
from pydlp.postprocessor.ffmpeg import has_ffmpeg


class SponsorBlockPostProcessor(BasePostProcessor):
    """Processes SponsorBlock segments (marking chapters or cutting out sponsor chunks)."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.api = SponsorBlockAPI(http_client)

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        remove_cats = self.options.get("sponsorblock_remove")
        mark_cats = self.options.get("sponsorblock_mark")

        if not remove_cats and not mark_cats:
            return files_to_delete, info

        # Only applicable for YouTube extractor
        if "youtube" not in (info.extractor or "").lower():
            return files_to_delete, info

        video_id = info.id
        requested_cats = list(set((remove_cats or []) + (mark_cats or [])))
        if "all" in requested_cats:
            requested_cats = None

        segments = self.api.get_segments(video_id, requested_cats)
        if not segments:
            return files_to_delete, info

        # 1. Mark as chapters
        if mark_cats:
            for s in segments:
                if "all" in mark_cats or s.category in mark_cats:
                    info.chapters.append(
                        MediaChapter(
                            title=f"[{s.category.upper()}] SponsorBlock",
                            start_time=s.start_time,
                            end_time=s.end_time,
                        )
                    )

        # 2. Cut out sponsor segments
        if remove_cats and has_ffmpeg(self.options.get("ffmpeg_location")):
            filepath = info.filepath or info.filename
            if not filepath or not os.path.exists(filepath):
                return files_to_delete, info

            to_remove = [
                s for s in segments if ("all" in remove_cats or s.category in remove_cats)
            ]
            if not to_remove:
                return files_to_delete, info

            total_dur = info.duration or 36000.0
            keep_intervals: List[Tuple[float, float]] = []
            curr_pos = 0.0

            for s in to_remove:
                if s.start_time > curr_pos:
                    keep_intervals.append((curr_pos, s.start_time))
                curr_pos = max(curr_pos, s.end_time)

            if curr_pos < total_dur:
                keep_intervals.append((curr_pos, total_dur))

            if not keep_intervals:
                return files_to_delete, info

            # Slice and concat with ffmpeg
            base_stem, ext = os.path.splitext(filepath)
            out_clean = f"{base_stem}.clean{ext}"
            temp_dir = tempfile.mkdtemp(prefix="pydlp_sb_")
            part_files = []

            try:
                ffmpeg_bin = self.options.get("ffmpeg_location") or "ffmpeg"
                for i, (start_t, end_t) in enumerate(keep_intervals):
                    dur = end_t - start_t
                    if dur < 0.2:
                        continue
                    part_out = os.path.join(temp_dir, f"part_{i:03d}{ext}")
                    cmd = [
                        ffmpeg_bin, "-y", "-ss", str(start_t), "-i", filepath,
                        "-t", str(dur), "-c", "copy", part_out,
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    part_files.append(part_out)

                if part_files:
                    # Concat list file
                    concat_list_path = os.path.join(temp_dir, "concat.txt")
                    with open(concat_list_path, "w", encoding="utf-8") as f:
                        for p in part_files:
                            f.write(f"file '{p}'\n")

                    concat_cmd = [
                        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0",
                        "-i", concat_list_path, "-c", "copy", out_clean,
                    ]
                    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                    if os.path.exists(out_clean):
                        files_to_delete.append(filepath)
                        os.replace(out_clean, filepath)
            except Exception:
                pass
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

        return files_to_delete, info
