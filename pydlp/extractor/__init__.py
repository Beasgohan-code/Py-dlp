"""Extractor registry and dispatch engine for Py-dlp."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from pydlp.core.exceptions import UnsupportedURLError
from pydlp.core.http import HttpClient
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.bandcamp import BandcampIE
from pydlp.extractor.base import InfoExtractor
from pydlp.extractor.bilibili import BilibiliIE
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.dailymotion import DailymotionIE
from pydlp.extractor.facebook import FacebookIE
from pydlp.extractor.generic import GenericIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.peertube import PeerTubeIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.rumble import RumbleIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.threads import ThreadsIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.twitch import TwitchIE
from pydlp.extractor.twitter import TwitterIE
from pydlp.extractor.vimeo import VimeoIE
from pydlp.extractor.youtube import YoutubeIE, YoutubePlaylistIE, YoutubeSearchIE

_BUILTIN_EXTRACTORS: List[Type[InfoExtractor]] = [
    YoutubePlaylistIE,
    YoutubeSearchIE,
    YoutubeIE,
    VimeoIE,
    TikTokIE,
    InstagramIE,
    TwitterIE,
    RedditIE,
    TwitchIE,
    SoundCloudIE,
    SpotifyIE,
    BilibiliIE,
    RumbleIE,
    DailymotionIE,
    FacebookIE,
    PinterestIE,
    ThreadsIE,
    BlueskyIE,
    StreamableIE,
    BandcampIE,
    PodcastIE,
    ArchiveOrgIE,
    PeerTubeIE,
    GenericIE,  # Must be last as fallback
]


def list_extractors() -> List[Type[InfoExtractor]]:
    """Returns all registered extractor classes including custom plugin extractors."""
    from pydlp.core.plugins import get_custom_extractors
    customs = get_custom_extractors()
    return customs + [e for e in _BUILTIN_EXTRACTORS if e not in customs]


def get_extractor_by_name(name: str) -> Optional[Type[InfoExtractor]]:
    """Finds an extractor by its exact IE_NAME or key."""
    clean = name.strip().lower()
    for ie in list_extractors():
        if ie.IE_NAME.lower() == clean or ie.ie_key().lower() == clean:
            return ie
    return None


def find_extractor_for_url(
    url: str,
    http_client: HttpClient,
    options: Optional[Dict[str, Any]] = None,
) -> InfoExtractor:
    """Finds and instantiates the first suitable extractor for a given URL."""
    clean_url = url.strip()
    for ie_class in list_extractors():
        if ie_class.suitable(clean_url):
            return ie_class(http_client, options)

    # Fallback to GenericIE
    return GenericIE(http_client, options)


__all__ = [
    "InfoExtractor",
    "GenericIE",
    "YoutubeIE",
    "YoutubePlaylistIE",
    "YoutubeSearchIE",
    "VimeoIE",
    "TikTokIE",
    "InstagramIE",
    "TwitterIE",
    "RedditIE",
    "TwitchIE",
    "SoundCloudIE",
    "SpotifyIE",
    "BilibiliIE",
    "RumbleIE",
    "DailymotionIE",
    "FacebookIE",
    "PinterestIE",
    "ThreadsIE",
    "BlueskyIE",
    "StreamableIE",
    "BandcampIE",
    "PodcastIE",
    "ArchiveOrgIE",
    "PeerTubeIE",
    "list_extractors",
    "get_extractor_by_name",
    "find_extractor_for_url",
]
