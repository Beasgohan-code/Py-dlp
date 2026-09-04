"""XHamster media extractor."""

from __future__ import annotations

import json
import re
from typing import List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class XHamsterIE(InfoExtractor):
    IE_NAME = "xhamster"
    IE_DESC = "XHamster video extractor"
    _VALID_URL = r"https?://(?:www\.|m\.)?xhamster\.(?:com|desi|one|xxx|pet|guru)/(?:videos|movies)/(?P<id>[^/?#&]+)"

    def _real_extract(self, url: str) -> MediaInfo:
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id=video_id)

        title = self._html_search_regex(
            [r'<h1[^>]*>(.+?)</h1>', r'<meta property="og:title" content="([^"]+)"'],
            webpage,
            "title",
            default=f"XHamster Video {video_id}",
        )
        title = re.sub(r"\s*-\s*xHamster(?:\.com)?\s*$", "", title, flags=re.IGNORECASE).strip()

        thumbnail = self._html_search_meta(["og:image", "twitter:image"], webpage)
        duration_s = self._search_regex(r'"duration"\s*:\s*(\d+)', webpage, "duration", default=None)
        duration = float(duration_s) if duration_s else None

        uploader = self._html_search_regex(
            [r'data-user-name="([^"]+)"', r'class="author-name"[^>]*>([^<]+)'],
            webpage,
            "uploader",
            default=None,
        )

        formats: List[MediaFormat] = []

        # Check for initial state or window.initials JSON
        init_json_match = re.search(r'window\.initials\s*=\s*(\{.+?\});\s*</script>', webpage)
        if init_json_match:
            try:
                data = json.loads(init_json_match.group(1))
                xplayer = data.get("xplayerSettings", {}) or data.get("videoModel", {})
                sources = xplayer.get("sources", {})
                if isinstance(sources, dict):
                    # HLS
                    hls_url = sources.get("hls", {}).get("url") if isinstance(sources.get("hls"), dict) else sources.get("hls")
                    if hls_url:
                        formats.extend(self._extract_m3u8_formats(hls_url, video_id=video_id, fatal=False))

                    # MP4 direct
                    mp4_sources = sources.get("mp4", {})
                    if isinstance(mp4_sources, dict):
                        for res, src in mp4_sources.items():
                            if isinstance(src, str) and src.startswith("http"):
                                height = int_or_none(res.replace("p", ""))
                                formats.append(
                                    MediaFormat(
                                        format_id=f"mp4-{res}",
                                        url=src,
                                        ext="mp4",
                                        height=height,
                                        format_note=f"MP4 {res}",
                                    )
                                )
                            elif isinstance(src, dict) and src.get("url"):
                                height = int_or_none(res.replace("p", ""))
                                formats.append(
                                    MediaFormat(
                                        format_id=f"mp4-{res}",
                                        url=src["url"],
                                        ext="mp4",
                                        height=height,
                                        format_note=f"MP4 {res}",
                                    )
                                )
            except Exception:
                pass

        # Regex fallback for embedded video URLs or sources
        if not formats:
            for m in re.finditer(r'["\'](?P<res>\d+p?)["\']\s*:\s*["\'](?P<url>https?://[^"\']+\.mp4[^"\']*)["\']', webpage):
                res = m.group("res")
                src = m.group("url")
                height = int_or_none(res.replace("p", ""))
                formats.append(
                    MediaFormat(
                        format_id=f"mp4-{res}",
                        url=src,
                        ext="mp4",
                        height=height,
                    )
                )

        if not formats:
            # Check for fallback .m3u8 or .mp4
            hls_match = re.search(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', webpage)
            if hls_match:
                formats.extend(self._extract_m3u8_formats(hls_match.group(1), video_id=video_id, fatal=False))

        return MediaInfo(
            id=video_id,
            title=title,
            webpage_url=url,
            duration=duration,
            thumbnail=thumbnail,
            uploader=uploader,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            formats=formats,
        )
