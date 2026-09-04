"""Extractor registry and dispatch engine for Py-dlp."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from pydlp.core.exceptions import UnsupportedURLError
from pydlp.core.http import HttpClient

# Extractors
from pydlp.extractor.abema import AbemaIE
from pydlp.extractor.afreecatv import AfreecaTVIE
from pydlp.extractor.animepahe import AnimePaheIE
from pydlp.extractor.aniwave import AniwaveIE
from pydlp.extractor.applepodcasts import ApplePodcastsIE
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.arte import ArteTVIE
from pydlp.extractor.audiomack import AudiomackIE
from pydlp.extractor.bandcamp import BandcampIE
from pydlp.extractor.base import InfoExtractor
from pydlp.extractor.bbc import BBCIE
from pydlp.extractor.beeg import BeegIE
from pydlp.extractor.bilibili import BilibiliIE
from pydlp.extractor.bitchute import BitChuteIE
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.brightcove import BrightcoveIE
from pydlp.extractor.camsoda import CamSodaIE
from pydlp.extractor.cbc import CBCIE
from pydlp.extractor.chaturbate import ChaturbateIE
from pydlp.extractor.chzzk import ChzzkIE
from pydlp.extractor.coub import CoubIE
from pydlp.extractor.coursera import CourseraIE
from pydlp.extractor.crunchyroll import CrunchyrollIE
from pydlp.extractor.cumlouder import CumlouderIE
from pydlp.extractor.dailymotion import DailymotionIE
from pydlp.extractor.deezer import DeezerIE
from pydlp.extractor.doodstream import DoodStreamIE
from pydlp.extractor.douyin import DouyinIE
from pydlp.extractor.dtube import DTubeIE
from pydlp.extractor.edx import EdXIE
from pydlp.extractor.eporner import EpornerIE
from pydlp.extractor.facebook import FacebookIE
from pydlp.extractor.fapello import FapelloIE
from pydlp.extractor.filemoon import FilemoonIE
from pydlp.extractor.france_tv import FranceTVIE
from pydlp.extractor.freesound import FreesoundIE
from pydlp.extractor.gdrive import GDriveIE
from pydlp.extractor.generic import GenericIE
from pydlp.extractor.giphy import GiphyIE
from pydlp.extractor.gogoanime import GogoAnimeIE
from pydlp.extractor.hanime import HanimeIE
from pydlp.extractor.hentaihaven import HentaiHavenIE
from pydlp.extractor.hqporner import HQPornerIE
from pydlp.extractor.imgur import ImgurIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.jwplayer import JWPlayerIE
from pydlp.extractor.khanacademy import KhanAcademyIE
from pydlp.extractor.kick import KickIE
from pydlp.extractor.likee import LikeeIE
from pydlp.extractor.linkedin import LinkedInIE
from pydlp.extractor.loom import LoomIE
from pydlp.extractor.manyvids import ManyVidsIE
from pydlp.extractor.mastodon import MastodonIE
from pydlp.extractor.medaltv import MedalTVIE
from pydlp.extractor.mediafire import MediaFireIE
from pydlp.extractor.mixcloud import MixcloudIE
from pydlp.extractor.mixdrop import MixdropIE
from pydlp.extractor.mixlr import MixlrIE
from pydlp.extractor.motherless import MotherlessIE
from pydlp.extractor.nebula import NebulaIE
from pydlp.extractor.nhk import NHKIE
from pydlp.extractor.niconico import NiconicoIE
from pydlp.extractor.ninegag import NineGagIE
from pydlp.extractor.odysee import OdyseeIE
from pydlp.extractor.peertube import PeerTubeIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.pornhub import PornhubIE
from pydlp.extractor.porntrex import PornTrexIE
from pydlp.extractor.rai import RaiPlayIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.redtube import RedTubeIE
from pydlp.extractor.rtbf import RTBFIE
from pydlp.extractor.rule34video import Rule34VideoIE
from pydlp.extractor.rumble import RumbleIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.spankbang import SpankBangIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.streamsb import StreamSBIE
from pydlp.extractor.streamtape import StreamtapeIE
from pydlp.extractor.ted import TedIE
from pydlp.extractor.threads import ThreadsIE
from pydlp.extractor.thumbzilla import ThumbzillaIE
from pydlp.extractor.tidal import TidalIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.tnaflix import TnaFlixIE
from pydlp.extractor.torrent import TorrentExtractor
from pydlp.extractor.trovo import TrovoIE
from pydlp.extractor.tube8 import Tube8IE
from pydlp.extractor.tunein import TuneInIE
from pydlp.extractor.twitch import TwitchIE
from pydlp.extractor.twitter import TwitterIE
from pydlp.extractor.udemy import UdemyIE
from pydlp.extractor.veoh import VeohIE
from pydlp.extractor.vidyard import VidyardIE
from pydlp.extractor.vimeo import VimeoIE
from pydlp.extractor.vk import VKIE
from pydlp.extractor.voe import VoeIE
from pydlp.extractor.wistia import WistiaIE
from pydlp.extractor.xhamster import XHamsterIE
from pydlp.extractor.xvideos import XVideosIE
from pydlp.extractor.youjizz import YouJizzIE
from pydlp.extractor.youtube import YoutubeIE, YoutubePlaylistIE, YoutubeSearchIE
from pydlp.extractor.zdf_ard import ZDFARDMediathekIE

_BUILTIN_EXTRACTORS: List[Type[InfoExtractor]] = [
    # YouTube & Search
    YoutubePlaylistIE,
    YoutubeSearchIE,
    YoutubeIE,
    # Anime & Animation
    AnimePaheIE,
    CrunchyrollIE,
    AniwaveIE,
    GogoAnimeIE,
    HentaiHavenIE,
    HanimeIE,
    # Adult Sites & Networks
    PornhubIE,
    XVideosIE,
    XHamsterIE,
    SpankBangIE,
    RedTubeIE,
    YouJizzIE,
    EpornerIE,
    MotherlessIE,
    BeegIE,
    Tube8IE,
    TnaFlixIE,
    PornTrexIE,
    ThumbzillaIE,
    ManyVidsIE,
    FapelloIE,
    CumlouderIE,
    ChaturbateIE,
    CamSodaIE,
    Rule34VideoIE,
    HQPornerIE,
    # Video Hosts & Cyberlockers
    StreamtapeIE,
    MixdropIE,
    DoodStreamIE,
    VoeIE,
    FilemoonIE,
    StreamSBIE,
    GDriveIE,
    MediaFireIE,
    # Global TV & News Broadcasters
    ArteTVIE,
    BBCIE,
    CBCIE,
    RaiPlayIE,
    RTBFIE,
    NHKIE,
    FranceTVIE,
    ZDFARDMediathekIE,
    # Education & Learning
    CourseraIE,
    KhanAcademyIE,
    EdXIE,
    UdemyIE,
    # Gaming & Esports Live Streams
    KickIE,
    TwitchIE,
    TrovoIE,
    AfreecaTVIE,
    ChzzkIE,
    MedalTVIE,
    # Enterprise & Video Hosting
    LoomIE,
    WistiaIE,
    BrightcoveIE,
    JWPlayerIE,
    NebulaIE,
    VidyardIE,
    TedIE,
    VeohIE,
    # Alternative Video & Decentralized
    OdyseeIE,
    BitChuteIE,
    DTubeIE,
    NiconicoIE,
    AbemaIE,
    VKIE,
    # Social Media & Short-Form Video
    VimeoIE,
    TikTokIE,
    InstagramIE,
    TwitterIE,
    RedditIE,
    DouyinIE,
    PinterestIE,
    ThreadsIE,
    BlueskyIE,
    StreamableIE,
    LikeeIE,
    LinkedInIE,
    ImgurIE,
    GiphyIE,
    NineGagIE,
    CoubIE,
    MastodonIE,
    # Music, Audio & Podcasts
    SoundCloudIE,
    SpotifyIE,
    DeezerIE,
    ApplePodcastsIE,
    TidalIE,
    MixcloudIE,
    AudiomackIE,
    BandcampIE,
    FreesoundIE,
    TuneInIE,
    MixlrIE,
    PodcastIE,
    # Historical & Federated
    BilibiliIE,
    RumbleIE,
    DailymotionIE,
    FacebookIE,
    ArchiveOrgIE,
    PeerTubeIE,
    TorrentExtractor,
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
    "list_extractors",
    "get_extractor_by_name",
    "find_extractor_for_url",
]
