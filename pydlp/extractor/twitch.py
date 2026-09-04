"""Twitch clips, VODs, and live stream extractor."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import int_or_none, try_get
from pydlp.extractor.base import InfoExtractor


class TwitchIE(InfoExtractor):
    """Extractor for Twitch clips, VODs, and live streams."""

    IE_NAME = "twitch"
    IE_DESC = "Twitch.tv clips, videos, and live broadcasts"
    _VALID_URL = r"^(?:https?://)?(?:www\.|clips\.)?twitch\.tv/(?:videos/(?P<vod_id>\d+)|(?P<channel>[^/]+)/clip/(?P<clip_id>[a-zA-Z0-9_-]+)|(?P<clip_slug>[a-zA-Z0-9_-]+))"

    _GQL_CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"

    def _real_extract(self, url: str) -> MediaInfo:
        m = re.match(self._VALID_URL, url)
        clip_id = m.groupdict().get("clip_id") or m.groupdict().get("clip_slug")
        vod_id = m.groupdict().get("vod_id")
        channel = m.groupdict().get("channel")

        media_id = clip_id or vod_id or channel or "twitch_media"

        # Clip GQL Query
        if clip_id and not vod_id:
            gql_query = {
                "operationName": "VideoAccessToken_Clip",
                "variables": {"slug": clip_id},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cdc079879372d7147e82804033615550",
                    }
                },
            }
            headers = {
                "Client-ID": self._GQL_CLIENT_ID,
                "Content-Type": "application/json",
            }
            resp = self._download_json(
                "https://gql.twitch.tv/gql",
                video_id=clip_id,
                headers=headers,
                data=json.dumps(gql_query).encode("utf-8"),
                fatal=False,
            )

            title = f"Twitch Clip {clip_id}"
            thumbnail = None
            formats: List[MediaFormat] = []

            if resp:
                clip_data = try_get(resp, lambda x: x["data"]["clip"], dict)
                if clip_data:
                    title = clip_data.get("title", title)
                    thumbnail = clip_data.get("thumbnailURL")
                    playback_access_token = clip_data.get("playbackAccessToken", {})
                    token = playback_access_token.get("value")
                    sig = playback_access_token.get("signature")

                    video_qualities = clip_data.get("videoQualities", [])
                    for q in video_qualities:
                        source_url = q.get("sourceURL")
                        if source_url and token and sig:
                            q_url = f"{source_url}?sig={sig}&token={token}"
                            quality = q.get("quality")
                            formats.append(
                                MediaFormat(
                                    format_id=f"{quality}p" if quality else "clip",
                                    url=q_url,
                                    ext="mp4",
                                    height=int_or_none(quality),
                                    fps=float(q.get("frameRate", 30)),
                                    format_note=f"{quality}p",
                                )
                            )

            if formats:
                return MediaInfo(
                    id=clip_id,
                    title=title,
                    extractor=self.IE_NAME,
                    extractor_key=self.ie_key(),
                    webpage_url=url,
                    thumbnail=thumbnail,
                    formats=formats,
                )

        # Fallback webpage scraping
        webpage = self._download_webpage(url, video_id=media_id, fatal=False)
        title = self._html_search_meta(["og:title"], webpage, default=f"Twitch {media_id}")
        thumb = self._html_search_meta(["og:image"], webpage)
        og_video = self._html_search_meta(["og:video", "og:video:secure_url"], webpage)

        formats = []
        if og_video:
            formats.append(MediaFormat(format_id="og-video", url=og_video, ext="mp4"))

        return MediaInfo(
            id=media_id,
            title=title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            thumbnail=thumb,
            formats=formats,
        )
