"""Post-processor for auto-generating AI summaries and transcript notes."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.ai_summary import TranscriptAnalyzer
from pydlp.core.http import HttpClient
from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor


class AISummaryPostProcessor(BasePostProcessor):
    """Extracts transcripts and writes structured .summary.md notes."""

    def __init__(self, http_client: HttpClient, options: Optional[Dict[str, Any]] = None):
        super().__init__(options)
        self.http = http_client

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        if not self.options.get("ai_summary", False) and not self.options.get("auto_chapters", False):
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath:
            return files_to_delete, info

        # Find available subtitle/transcript text
        raw_text = ""
        all_subs = dict(info.subtitles)
        all_subs.update(info.automatic_captions)

        for lang in ("en", "en-US", "en-GB", "auto"):
            for k, track_list in all_subs.items():
                if k == lang or k.startswith("en"):
                    for track in track_list:
                        if track.data:
                            raw_text = track.data
                            break
                        elif track.url:
                            try:
                                resp = self.http.get(track.url)
                                raw_text = resp.text()
                                break
                            except Exception:
                                pass
                if raw_text:
                    break
            if raw_text:
                break

        if not raw_text:
            return files_to_delete, info

        analyzer = TranscriptAnalyzer(raw_text)

        # Auto-chapters
        if self.options.get("auto_chapters", False) and not info.chapters:
            info.chapters = analyzer.generate_auto_chapters()

        # Write .summary.md
        if self.options.get("ai_summary", False):
            base_stem, _ = os.path.splitext(filepath)
            summary_path = f"{base_stem}.summary.md"
            summary_content = analyzer.generate_summary(info.title, info.duration)
            try:
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(summary_content)
            except Exception:
                pass

        return files_to_delete, info
