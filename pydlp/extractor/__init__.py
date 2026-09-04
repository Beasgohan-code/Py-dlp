"""Extractor registry and dispatch engine for Py-dlp."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from pydlp.core.exceptions import UnsupportedURLError
from pydlp.core.http import HttpClient

# Extractors
from pydlp.extractor.abema import AbemaIE
from pydlp.extractor.animepahe import AnimePaheIE
from pydlp.extractor.aniwave import AniwaveIE
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.audiomack import AudiomackIE
from pydlp.extractor.bandcamp import BandcampIE
from pydlp.extractor.base import InfoExtractor
from pydlp.extractor.bilibili import BilibiliIE
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.brightcove import BrightcoveIE
from pydlp.extractor.chaturbate import ChaturbateIE
from pydlp.extractor.crunchyroll import CrunchyrollIE
from pydlp.extractor.dailymotion import DailymotionIE
from pydlp.extractor.deezer import DeezerIE
from pydlp.extractor.doodstream import DoodStreamIE
from pydlp.extractor.douyin import DouyinIE
from pydlp.extractor.eporner import EpornerIE
from pydlp.extractor.facebook import FacebookIE
from pydlp.extractor.filemoon import FilemoonIE
from pydlp.extractor.gdrive import GDriveIE
from pydlp.extractor.generic import GenericIE
from pydlp.extractor.gogoanime import GogoAnimeIE
from pydlp.extractor.hqporner import HQPornerIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.jwplayer import JWPlayerIE
from pydlp.extractor.kick import KickIE
from pydlp.extractor.loom import LoomIE
from pydlp.extractor.mixcloud import MixcloudIE
from pydlp.extractor.mixdrop import MixdropIE
from pydlp.extractor.nebula import NebulaIE
from pydlp.extractor.niconico import NiconicoIE
from pydlp.extractor.peertube import PeerTubeIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.pornhub import PornhubIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.redtube import RedTubeIE
from pydlp.extractor.rule34video import Rule34VideoIE
from pydlp.extractor.rumble import RumbleIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.spankbang import SpankBangIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.streamsb import StreamSBIE
from pydlp.extractor.streamtape import StreamtapeIE
from pydlp.extractor.threads import ThreadsIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.twitch import TwitchIE
from pydlp.extractor.twitter import TwitterIE
from pydlp.extractor.vimeo import VimeoIE
from pydlp.extractor.voe import VoeIE
from pydlp.extractor.wistia import WistiaIE
from pydlp.extractor.xvideos import XVideosIE
from pydlp.extractor.youtube import YoutubeIE, YoutubePlaylistIE, YoutubeSearchIE

_BUILTIN_EXTRACTORS: List[Type[InfoExtractor]] = [
    YoutubePlaylistIE,
    YoutubeSearchIE,
    YoutubeIE,
    AnimePaheIE,
    CrunchyrollIE,
    AniwaveIE,
    GogoAnimeIE,
    PornhubIE,
    XVideosIE,
    SpankBangIE,
    RedTubeIE,
    EpornerIE,
    ChaturbateIE,
    Rule34VideoIE,
    HQPornerIE,
    StreamtapeIE,
    MixdropIE,
    DoodStreamIE,
    VoeIE,
    FilemoonIE,
    StreamSBIE,
    GDriveIE,
    KickIE,
    NiconicoIE,
    AbemaIE,
    DouyinIE,
    LoomIE,
    WistiaIE,
    BrightcoveIE,
    JWPlayerIE,
    NebulaIE,
    VimeoIE,
    TikTokIE,
    InstagramIE,
    TwitterIE,
    RedditIE,
    TwitchIE,
    SoundCloudIE,
    SpotifyIE,
    DeezerIE,
    MixcloudIE,
    AudiomackIE,
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
    "AnimePaheIE",
    "CrunchyrollIE",
    "AniwaveIE",
    "GogoAnimeIE",
    "PornhubIE",
    "XVideosIE",
    "SpankBangIE",
    "RedTubeIE",
    "EpornerIE",
    "ChaturbateIE",
    "Rule34VideoIE",
    "HQPornerIE",
    "StreamtapeIE",
    "MixdropIE",
    "DoodStreamIE",
    "VoeIE",
    "FilemoonIE",
    "StreamSBIE",
    "GDriveIE",
    "KickIE",
    "NiconicoIE",
    "AbemaIE",
    "DouyinIE",
    "LoomIE",
    "WistiaIE",
    "BrightcoveIE",
    "JWPlayerIE",
    "NebulaIE",
    "VimeoIE",
    "TikTokIE",
    "InstagramIE",
    "TwitterIE",
    "RedditIE",
    "TwitchIE",
    "SoundCloudIE",
    "SpotifyIE",
    "DeezerIE",
    "MixcloudIE",
    "AudiomackIE",
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
