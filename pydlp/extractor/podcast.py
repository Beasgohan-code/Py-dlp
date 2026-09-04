"""Podcast and RSS feed extractor."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from pydlp.core.exceptions import ExtractorError
from pydlp.core.types import MediaFormat, MediaInfo, MediaThumbnail
from pydlp.core.utils import clean_html, determine_ext, int_or_none, parse_duration, parse_iso8601
from pydlp.extractor.base import InfoExtractor


class PodcastIE(InfoExtractor):
    """Extractor for Podcast RSS feeds and podcast episode URLs."""

    IE_NAME = "podcast"
    IE_DESC = "Podcast RSS feeds and episodes"
    _VALID_URL = r"^(?:https?://)?.+?(?:\.rss|\.xml|/feed|/rss|/podcast/rss|feeds\..+)"

    def _real_extract(self, url: str) -> MediaInfo:
        feed_xml = self._download_webpage(url, fatal=False)
        if not feed_xml or ("<rss" not in feed_xml and "<feed" not in feed_xml):
            raise ExtractorError(f"Not a valid podcast RSS feed: {url}")

        # Strip namespace for simplified parsing
        clean_xml_str = re.sub(r'\sxmlns(?::\w+)?="[^"]+"', "", feed_xml)
        root = ET.fromstring(clean_xml_str)

        channel = root.find("channel") or root
        channel_title = channel.findtext("title") or "Podcast Feed"
        channel_desc = channel.findtext("description")

        thumb_elem = channel.find("image/url") or channel.find("image")
        channel_thumb = thumb_elem.attrib.get("href") if thumb_elem is not None and "href" in thumb_elem.attrib else (thumb_elem.text if thumb_elem is not None else None)

        entries: List[MediaInfo] = []
        items = channel.findall("item") or channel.findall("entry")

        for idx, item in enumerate(items, 1):
            item_title = item.findtext("title") or f"Episode {idx}"
            item_desc = item.findtext("description")
            pub_date = item.findtext("pubDate") or item.findtext("published")
            upload_date, timestamp = parse_iso8601(pub_date)
            dur_str = item.findtext("duration")
            duration = parse_duration(dur_str)

            # Enclosure
            enclosure = item.find("enclosure")
            enc_url = None
            enc_type = "audio/mpeg"
            enc_len = None

            if enclosure is not None:
                enc_url = enclosure.attrib.get("url")
                enc_type = enclosure.attrib.get("type", "audio/mpeg")
                enc_len = int_or_none(enclosure.attrib.get("length"))
            else:
                # Atom link
                link = item.find("link[@rel='enclosure']")
                if link is not None:
                    enc_url = link.attrib.get("href")
                    enc_type = link.attrib.get("type", "audio/mpeg")

            if enc_url:
                ext = determine_ext(enc_url, "mp3")
                is_video = "video" in enc_type or ext in ("mp4", "m4v", "mov")

                fmt = MediaFormat(
                    format_id="enclosure",
                    url=enc_url,
                    ext=ext,
                    filesize=enc_len,
                    vcodec="none" if not is_video else None,
                    acodec="mp3" if not is_video else None,
                )

                entries.append(
                    MediaInfo(
                        id=f"ep_{idx}",
                        title=item_title,
                        extractor="podcast:episode",
                        extractor_key="PodcastEpisode",
                        webpage_url=enc_url,
                        description=item_desc,
                        upload_date=upload_date,
                        timestamp=timestamp,
                        duration=duration,
                        thumbnail=channel_thumb,
                        formats=[fmt],
                        playlist_id=url,
                        playlist_title=channel_title,
                        playlist_index=idx,
                    )
                )

        return MediaInfo(
            id="feed",
            title=channel_title,
            extractor=self.IE_NAME,
            extractor_key=self.ie_key(),
            webpage_url=url,
            description=channel_desc,
            thumbnail=channel_thumb,
            _type="playlist",
            playlist_id=url,
            playlist_title=channel_title,
            playlist_count=len(entries),
            entries=entries,
        )
