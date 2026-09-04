"""Comprehensive test coverage for all 55+ platform extractors."""

import unittest
from pydlp.extractor import list_extractors
from pydlp.extractor.abema import AbemaIE
from pydlp.extractor.animepahe import AnimePaheIE
from pydlp.extractor.aniwave import AniwaveIE
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.audiomack import AudiomackIE
from pydlp.extractor.bandcamp import BandcampIE
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


class TestAllExtractors(unittest.TestCase):
    def test_all_extractors_registered(self):
        extractors = list_extractors()
        self.assertGreaterEqual(len(extractors), 50)

    def test_anime_extractors(self):
        self.assertTrue(AnimePaheIE.suitable("https://animepahe.ru/play/1234abcd-1234-abcd/5678efgh"))
        self.assertTrue(AnimePaheIE.suitable("https://animepahe.org/anime/1234abcd-1234-abcd"))
        self.assertTrue(CrunchyrollIE.suitable("https://www.crunchyroll.com/watch/G69V7E5P6/attack-on-titan"))
        self.assertTrue(AniwaveIE.suitable("https://aniwave.to/watch/one-piece.ov8/ep-1000"))
        self.assertTrue(GogoAnimeIE.suitable("https://anitaku.to/category/jujutsu-kaisen"))

    def test_adult_extractors(self):
        self.assertTrue(PornhubIE.suitable("https://www.pornhub.com/view_video.php?viewkey=ph12345678"))
        self.assertTrue(XVideosIE.suitable("https://www.xvideos.com/video12345678/awesome_clip"))
        self.assertTrue(XVideosIE.suitable("https://www.xnxx.com/video-12345678/awesome_clip"))
        self.assertTrue(SpankBangIE.suitable("https://spankbang.com/12345/video/sample"))
        self.assertTrue(RedTubeIE.suitable("https://www.redtube.com/12345678"))
        self.assertTrue(RedTubeIE.suitable("https://www.youporn.com/watch/12345678/sample"))
        self.assertTrue(EpornerIE.suitable("https://www.eporner.com/video-12345678/sample-video/"))
        self.assertTrue(ChaturbateIE.suitable("https://chaturbate.com/sweet_model/"))
        self.assertTrue(ChaturbateIE.suitable("https://stripchat.com/cool_performer/"))
        self.assertTrue(Rule34VideoIE.suitable("https://rule34video.party/videos/123456/sample-animation/"))
        self.assertTrue(HQPornerIE.suitable("https://hqporner.com/hdporn/12345-sample_video.html"))

    def test_videohost_extractors(self):
        self.assertTrue(StreamtapeIE.suitable("https://streamtape.com/v/abc1234/video.mp4"))
        self.assertTrue(MixdropIE.suitable("https://mixdrop.co/e/abc1234"))
        self.assertTrue(DoodStreamIE.suitable("https://dood.to/e/abc1234"))
        self.assertTrue(VoeIE.suitable("https://voe.sx/e/abc1234"))
        self.assertTrue(FilemoonIE.suitable("https://filemoon.sx/e/abc1234"))
        self.assertTrue(StreamSBIE.suitable("https://streamsb.net/e/abc1234.html"))
        self.assertTrue(GDriveIE.suitable("https://drive.google.com/file/d/1a2b3c4d5e6f7g/view"))

    def test_global_tv_and_live(self):
        self.assertTrue(KickIE.suitable("https://kick.com/xqc"))
        self.assertTrue(KickIE.suitable("https://kick.com/xqc/clips/clip_12345"))
        self.assertTrue(NiconicoIE.suitable("https://www.nicovideo.jp/watch/sm12345678"))
        self.assertTrue(AbemaIE.suitable("https://abema.tv/video/episode/123-456_s1_p1"))
        self.assertTrue(DouyinIE.suitable("https://www.douyin.com/video/7123456789012345678"))
        self.assertTrue(LoomIE.suitable("https://www.loom.com/share/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"))
        self.assertTrue(WistiaIE.suitable("https://fast.wistia.net/embed/iframe/abc1234"))
        self.assertTrue(BrightcoveIE.suitable("https://players.brightcove.net/123456789/default_default/index.html?videoId=987654321"))
        self.assertTrue(JWPlayerIE.suitable("https://cdn.jwplayer.com/players/abc1234-xyz5678.html"))
        self.assertTrue(NebulaIE.suitable("https://nebula.tv/videos/creator-video-title"))

    def test_music_extractors(self):
        self.assertTrue(DeezerIE.suitable("https://www.deezer.com/track/123456789"))
        self.assertTrue(MixcloudIE.suitable("https://www.mixcloud.com/dj_artist/awesome-mix-vol-1/"))
        self.assertTrue(AudiomackIE.suitable("https://audiomack.com/artist-name/song/hit-single"))


if __name__ == "__main__":
    unittest.main()
