"""Brightcove video embed extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, int_or_none, parse_duration
from pydlp.extractor.base import InfoExtractor


class BrightcoveIE(InfoExtractor):
    """Extractor for Brightcove embedded videos."""

    IE_NAME = "brightcove"
    IE_DESC = "Brightcove.com embedded players"
    _VALID_URL = r"^(?:https?://)?(?:players|edge)\.brightcove\.net/(?P<account>\d+)/(?P<player>[^/]+)_default/index\.html\?videoId=(?P<id>\d+)"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        account_id = m.group("account")
        video_id = m.group("id")

        # Edge Playback API
        api_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{account_id}/videos/{video_id}"
        headers = {
            "Accept": "application/json;pk=BCpkADawqM0NKZydTWhdaqG4GdYgjUWmWchdpFM6h30xSinglePolicyKey",
        }
        data = self._download_json(api_url, video_id=video_id, headers=headers, fatal=False)

        title = f"Brightcove Video {video_id}"
        thumbnail = None
        duration = None
        formats: List[MediaFormat] = []

        if data:
            title = data.get("name", title)
            thumbnail = data.get("thumbnail")
            duration = data.get("duration", 0) / 1000.0 if data.get("duration") else None

            sources = data.get("sources", [])
            for s in sources:
                src_url = s.get("src")
                if not src_url:
                    continue
                c_type = s.get("container", "")
                if ".m3u8" in src_url or "hls" in c_type:
                    formats.extend(self._extract_m3u8_formats(src_url, video_id))
                elif ".mpd" in src_url:
                    formats.extend(self._extract_mpd_formats(src_url, video_id))
                else:
                    w = int_or_none(s.get("width"))
                    h = int_or_none(s.get("height"))
                    bitrate = int_or_none(s.get("avg_bitrate"))
                    formats.append(
                        MediaFormat(
                            format_id=f"http-{h}p" if h else f"src-{len(formats)}",
                            url=src_url,
                            ext="mp4",
                            width=w,
                            height=h,
                            tbr=round(bitrate / 1000.0, 1) if bitrate else None,
                        )
                    )

        if not formats:
            formats.append(MediaFormat(format_id="direct", url=url, ext="mp4"))

        return MediaInfo(
            id=video_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumbnail,
            duration=duration,
            formats=formats,
        )
