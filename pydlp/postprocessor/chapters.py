"""Chapter marker post-processor for exporting chapters."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from pydlp.core.types import MediaInfo
from pydlp.postprocessor.base import BasePostProcessor


class ChapterPostProcessor(BasePostProcessor):
    """Exports chapter markers to JSON or FFmetadata files."""

    def run(self, info: MediaInfo) -> Tuple[List[str], MediaInfo]:
        files_to_delete: List[str] = []
        if not info.chapters:
            return files_to_delete, info

        filepath = info.filepath or info.filename
        if not filepath:
            return files_to_delete, info

        base_stem, _ = os.path.splitext(filepath)

        # Export chapters JSON
        if self.options.get("writechapters", False):
            out_chapters_path = f"{base_stem}.chapters.json"
            try:
                data = [c.to_dict() for c in info.chapters]
                with open(out_chapters_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                pass

        return files_to_delete, info
