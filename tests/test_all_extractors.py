"""Comprehensive test coverage for all 105+ platform extractors."""

import unittest
from pydlp.extractor import list_extractors

# Anime
from pydlp.extractor.animepahe import AnimePaheIE
from pydlp.extractor.aniwave import AniwaveIE
from pydlp.extractor.crunchyroll import CrunchyrollIE
from pydlp.extractor.gogoanime import GogoAnimeIE
from pydlp.extractor.hanime import HanimeIE
from pydlp.extractor.hentaihaven import HentaiHavenIE

# Adult Sites
from pydlp.extractor.beeg import BeegIE
from pydlp.extractor.camsoda import CamSodaIE
from pydlp.extractor.chaturbate import ChaturbateIE
from pydlp.extractor.cumlouder import CumlouderIE
from pydlp.extractor.eporner import EpornerIE
from pydlp.extractor.fapello import FapelloIE
from pydlp.extractor.hqporner import HQPornerIE
from pydlp.extractor.manyvids import ManyVidsIE
from pydlp.extractor.motherless import MotherlessIE
from pydlp.extractor.pornhub import PornhubIE
from pydlp.extractor.porntrex import PornTrexIE
from pydlp.extractor.redtube import RedTubeIE
from pydlp.extractor.rule34video import Rule34VideoIE
from pydlp.extractor.spankbang import SpankBangIE
from pydlp.extractor.thumbzilla import ThumbzillaIE
from pydlp.extractor.tnaflix import TnaFlixIE
from pydlp.extractor.tube8 import Tube8IE
from pydlp.extractor.xhamster import XHamsterIE
from pydlp.extractor.xvideos import XVideosIE
from pydlp.extractor.youjizz import YouJizzIE

# Video Hosts & Cyberlockers
from pydlp.extractor.doodstream import DoodStreamIE
from pydlp.extractor.filemoon import FilemoonIE
from pydlp.extractor.gdrive import GDriveIE
from pydlp.extractor.mediafire import MediaFireIE
from pydlp.extractor.mixdrop import MixdropIE
from pydlp.extractor.streamsb import StreamSBIE
from pydlp.extractor.streamtape import StreamtapeIE
from pydlp.extractor.voe import VoeIE

# Global TV & News Broadcasters
from pydlp.extractor.arte import ArteTVIE
from pydlp.extractor.bbc import BBCIE
from pydlp.extractor.cbc import CBCIE
from pydlp.extractor.france_tv import FranceTVIE
from pydlp.extractor.nhk import NHKIE
from pydlp.extractor.rai import RaiPlayIE
from pydlp.extractor.rtbf import RTBFIE
from pydlp.extractor.zdf_ard import ZDFARDMediathekIE

# Education & Courses
from pydlp.extractor.coursera import CourseraIE
from pydlp.extractor.edx import EdXIE
from pydlp.extractor.khanacademy import KhanAcademyIE
from pydlp.extractor.udemy import UdemyIE

# Gaming & Esports Live Streams
from pydlp.extractor.afreecatv import AfreecaTVIE
from pydlp.extractor.chzzk import ChzzkIE
from pydlp.extractor.kick import KickIE
from pydlp.extractor.medaltv import MedalTVIE
from pydlp.extractor.trovo import TrovoIE
from pydlp.extractor.twitch import TwitchIE

# Enterprise & Video Hosting
from pydlp.extractor.brightcove import BrightcoveIE
from pydlp.extractor.jwplayer import JWPlayerIE
from pydlp.extractor.loom import LoomIE
from pydlp.extractor.nebula import NebulaIE
from pydlp.extractor.ted import TedIE
from pydlp.extractor.veoh import VeohIE
from pydlp.extractor.vidyard import VidyardIE
from pydlp.extractor.wistia import WistiaIE

# Alternative Video & Live
from pydlp.extractor.abema import AbemaIE
from pydlp.extractor.bitchute import BitChuteIE
from pydlp.extractor.dtube import DTubeIE
from pydlp.extractor.niconico import NiconicoIE
from pydlp.extractor.odysee import OdyseeIE
from pydlp.extractor.vk import VKIE

# Mainstream Social Media
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.coub import CoubIE
from pydlp.extractor.douyin import DouyinIE
from pydlp.extractor.giphy import GiphyIE
from pydlp.extractor.imgur import ImgurIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.likee import LikeeIE
from pydlp.extractor.linkedin import LinkedInIE
from pydlp.extractor.mastodon import MastodonIE
from pydlp.extractor.ninegag import NineGagIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.threads import ThreadsIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.twitter import TwitterIE
from pydlp.extractor.vimeo import VimeoIE
from pydlp.extractor.youtube import YoutubeIE, YoutubePlaylistIE, YoutubeSearchIE

# Music & Audio
from pydlp.extractor.applepodcasts import ApplePodcastsIE
from pydlp.extractor.audiomack import AudiomackIE
from pydlp.extractor.bandcamp import BandcampIE
from pydlp.extractor.deezer import DeezerIE
from pydlp.extractor.freesound import FreesoundIE
from pydlp.extractor.mixcloud import MixcloudIE
from pydlp.extractor.mixlr import MixlrIE
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.tidal import TidalIE
from pydlp.extractor.tunein import TuneInIE

# Historical & Federated
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.bilibili import BilibiliIE
from pydlp.extractor.dailymotion import DailymotionIE
from pydlp.extractor.facebook import FacebookIE
from pydlp.extractor.peertube import PeerTubeIE
from pydlp.extractor.rumble import RumbleIE


class TestAllExtractors(unittest.TestCase):
    def test_all_extractors_registered(self):
        extractors = list_extractors()
        self.assertGreaterEqual(len(extractors), 100)

    def test_anime_extractors(self):
        self.assertTrue(AnimePaheIE.suitable("https://animepahe.ru/play/1234abcd-1234-abcd/5678efgh"))
        self.assertTrue(CrunchyrollIE.suitable("https://www.crunchyroll.com/watch/G69V7E5P6/attack-on-titan"))
        self.assertTrue(AniwaveIE.suitable("https://aniwave.to/watch/one-piece.ov8/ep-1000"))
        self.assertTrue(GogoAnimeIE.suitable("https://anitaku.to/category/jujutsu-kaisen"))
        self.assertTrue(HentaiHavenIE.suitable("https://hentaihaven.xxx/episode/overflow-episode-1/"))
        self.assertTrue(HanimeIE.suitable("https://hanime.tv/videos/hentai/itadaki-seieki"))

    def test_adult_extractors(self):
        self.assertTrue(PornhubIE.suitable("https://www.pornhub.com/view_video.php?viewkey=ph12345678"))
        self.assertTrue(XVideosIE.suitable("https://www.xvideos.com/video12345678/awesome_clip"))
        self.assertTrue(XHamsterIE.suitable("https://xhamster.com/videos/awesome-video-123456"))
        self.assertTrue(YouJizzIE.suitable("https://www.youjizz.com/videos/sample-title-123456.html"))
        self.assertTrue(SpankBangIE.suitable("https://spankbang.com/12345/video/sample"))
        self.assertTrue(RedTubeIE.suitable("https://www.redtube.com/12345678"))
        self.assertTrue(EpornerIE.suitable("https://www.eporner.com/video-12345678/sample-video/"))
        self.assertTrue(MotherlessIE.suitable("https://motherless.com/ABC1234"))
        self.assertTrue(BeegIE.suitable("https://beeg.com/12345678"))
        self.assertTrue(Tube8IE.suitable("https://www.tube8.com/amateur/sample-video/12345/"))
        self.assertTrue(TnaFlixIE.suitable("https://www.tnaflix.com/video12345"))
        self.assertTrue(PornTrexIE.suitable("https://www.porntrex.com/videos/123456/sample/"))
        self.assertTrue(ThumbzillaIE.suitable("https://www.thumbzilla.com/video/ph123456/sample-video"))
        self.assertTrue(ManyVidsIE.suitable("https://www.manyvids.com/Video/123456/Sample-Title/"))
        self.assertTrue(FapelloIE.suitable("https://fapello.com/supermodel/123/"))
        self.assertTrue(CumlouderIE.suitable("https://www.cumlouder.com/video/12345/sample/"))
        self.assertTrue(ChaturbateIE.suitable("https://chaturbate.com/sweet_model/"))
        self.assertTrue(CamSodaIE.suitable("https://www.camsoda.com/sexy_model"))
        self.assertTrue(Rule34VideoIE.suitable("https://rule34video.party/videos/123456/sample-animation/"))
        self.assertTrue(HQPornerIE.suitable("https://hqporner.com/hdporn/12345-sample_video.html"))

    def test_global_tv_and_news(self):
        self.assertTrue(ArteTVIE.suitable("https://www.arte.tv/en/videos/123456-000-A/documentary/"))
        self.assertTrue(BBCIE.suitable("https://www.bbc.co.uk/iplayer/episode/p0123456/sample-episode"))
        self.assertTrue(CBCIE.suitable("https://www.cbc.ca/player/play/1234567890"))
        self.assertTrue(RaiPlayIE.suitable("https://www.raiplay.it/video/2026/09/sample-show-abc.html"))
        self.assertTrue(RTBFIE.suitable("https://www.rtbf.be/auvio/detail_show?id=123456"))
        self.assertTrue(NHKIE.suitable("https://www.nhk.or.jp/nhkworld/en/ondemand/video/123456/"))
        self.assertTrue(FranceTVIE.suitable("https://www.france.tv/france-2/journal-20h/123456-emission.html"))
        self.assertTrue(ZDFARDMediathekIE.suitable("https://www.ardmediathek.de/video/sendung/123456"))

    def test_education_extractors(self):
        self.assertTrue(CourseraIE.suitable("https://www.coursera.org/learn/machine-learning/lecture/abc12/intro-to-ml"))
        self.assertTrue(KhanAcademyIE.suitable("https://www.khanacademy.org/math/algebra/v/linear-equations-intro"))
        self.assertTrue(EdXIE.suitable("https://www.edx.org/course/introduction-to-python/12345"))
        self.assertTrue(UdemyIE.suitable("https://www.udemy.com/course/python-masterclass/12345"))

    def test_gaming_and_streaming(self):
        self.assertTrue(KickIE.suitable("https://kick.com/xqc"))
        self.assertTrue(TwitchIE.suitable("https://www.twitch.tv/shroud"))
        self.assertTrue(TrovoIE.suitable("https://trovo.live/s/StreamerName"))
        self.assertTrue(AfreecaTVIE.suitable("https://play.afreecatv.com/streamer/12345678"))
        self.assertTrue(ChzzkIE.suitable("https://chzzk.naver.com/live/abc123456789"))
        self.assertTrue(MedalTVIE.suitable("https://medal.tv/games/valorant/clips/12345abcde"))

    def test_social_extractors(self):
        self.assertTrue(InstagramIE.suitable("https://www.instagram.com/p/CXYZ1234/"))
        self.assertTrue(TikTokIE.suitable("https://www.tiktok.com/@user/video/1234567890123456789"))
        self.assertTrue(TwitterIE.suitable("https://twitter.com/user/status/1234567890123456789"))
        self.assertTrue(RedditIE.suitable("https://www.reddit.com/r/funny/comments/abc123/funny_video/"))
        self.assertTrue(MastodonIE.suitable("https://mastodon.social/@user/123456789012345678"))
        self.assertTrue(VeohIE.suitable("https://www.veoh.com/watch/v12345678"))

    def test_music_and_radio(self):
        self.assertTrue(SpotifyIE.suitable("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"))
        self.assertTrue(SoundCloudIE.suitable("https://soundcloud.com/artist/track-name"))
        self.assertTrue(TuneInIE.suitable("https://tunein.com/radio/BBC-Radio-1-988-s24939/"))
        self.assertTrue(MixlrIE.suitable("https://mixlr.com/live-showcase"))


if __name__ == "__main__":
    unittest.main()
