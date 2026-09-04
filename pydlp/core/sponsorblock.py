"""SponsorBlock API client and segment data structures."""

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydlp.core.http import HttpClient

DEFAULT_CATEGORIES = [
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "music_offtopic",
]


@dataclass
class SponsorSegment:
    category: str
    start_time: float
    end_time: float
    uuid: Optional[str] = None

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "uuid": self.uuid,
        }


class SponsorBlockAPI:
    """Client for fetching crowd-sourced sponsor and filler timestamps from SponsorBlock API."""

    API_BASE = "https://sponsor.ajay.app/api/skipSegments"

    def __init__(self, http_client: HttpClient):
        self.http = http_client

    def get_segments(
        self, video_id: str, categories: Optional[List[str]] = None
    ) -> List[SponsorSegment]:
        """Fetches sponsor segments for a YouTube video ID."""
        cats = categories or DEFAULT_CATEGORIES
        categories_json = json.dumps(cats)
        query = urllib.parse.urlencode(
            {"videoID": video_id, "categories": categories_json}
        )
        url = f"{self.API_BASE}?{query}"

        try:
            resp = self.http.get(url, timeout=5.0)
            if resp.status_code != 200:
                return []
            data = resp.json()
            if not isinstance(data, list):
                return []

            segments: List[SponsorSegment] = []
            for item in data:
                cat = item.get("category", "sponsor")
                seg = item.get("segment", [])
                if len(seg) >= 2:
                    start_t = float(seg[0])
                    end_t = float(seg[1])
                    segments.append(
                        SponsorSegment(
                            category=cat,
                            start_time=start_t,
                            end_time=end_t,
                            uuid=item.get("UUID"),
                        )
                    )
            return sorted(segments, key=lambda s: s.start_time)
        except Exception:
            return []
