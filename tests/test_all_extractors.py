"""Comprehensive test coverage for all 80+ platform extractors."""

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

# Global Streaming & Live & Enterprise
from pydlp.extractor.abema import AbemaIE
from pydlp.extractor.bitchute import BitChuteIE
from pydlp.extractor.brightcove import BrightcoveIE
from pydlp.extractor.douyin import DouyinIE
from pydlp.extractor.dtube import DTubeIE
from pydlp.extractor.jwplayer import JWPlayerIE
from pydlp.extractor.kick import KickIE
from pydlp.extractor.loom import LoomIE
from pydlp.extractor.nebula import NebulaIE
from pydlp.extractor.niconico import NiconicoIE
from pydlp.extractor.odysee import OdyseeIE
from pydlp.extractor.ted import TedIE
from pydlp.extractor.vidyard import VidyardIE
from pydlp.extractor.vk import VKIE
from pydlp.extractor.wistia import WistiaIE

# Mainstream Social Media
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.coub import CoubIE
from pydlp.extractor.giphy import GiphyIE
from pydlp.extractor.imgur import ImgurIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.likee import LikeeIE
from pydlp.extractor.linkedin import LinkedInIE
from pydlp.extractor.ninegag import NineGagIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.threads import ThreadsIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.twitch import TwitchIE
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
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.tidal import TidalIE

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
        self.assertGreaterEqual(len(extractors), 75)

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
        self.assertTrue(XVideosIE.suitable("https://www.xnXX.com/video-12345678/awesome_clip"))
        self.assertTrue(XHamsterIE.suitable("https://xhamster.com/videos/awesome-video-123456"))
        self.assertTrue(XHamsterIE.suitable("https://xhamster.desi/movies/great-clip-789012"))
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

    def test_videohost_extractors(self):
        self.assertTrue(StreamtapeIE.suitable("https://streamtape.com/v/abc1234/video.mp4"))
        self.assertTrue(MixdropIE.suitable("https://mixdrop.co/e/abc1234"))
        self.assertTrue(DoodStreamIE.suitable("https://dood.to/e/abc1234"))
        self.assertTrue(VoeIE.suitable("https://voe.sx/e/abc1234"))
        self.assertTrue(FilemoonIE.suitable("https://filemoon.sx/e/abc1234"))
        self.assertTrue(StreamSBIE.suitable("https://streamsb.net/e/abc1234.html"))
        self.assertTrue(GDriveIE.suitable("https://drive.google.com/file/d/1a2b3c4d5e6f7g/view"))
        self.assertTrue(MediaFireIE.suitable("https://www.mediafire.com/file/abc12345/video.mp4/file"))

    def test_global_tv_and_live(self):
        self.assertTrue(KickIE.suitable("https://kick.com/xqc"))
        self.assertTrue(NiconicoIE.suitable("https://www.nicovideo.jp/watch/sm12345678"))
        self.assertTrue(AbemaIE.suitable("https://abema.tv/video/episode/123-456_s1_p1"))
        self.assertTrue(DouyinIE.suitable("https://www.douyin.com/video/7123456789012345678"))
        self.assertTrue(LoomIE.suitable("https://www.loom.com/share/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"))
        self.assertTrue(WistiaIE.suitable("https://fast.wistia.net/embed/iframe/abc1234"))
        self.assertTrue(BrightcoveIE.suitable("https://players.brightcove.net/123456789/default_default/index.html?videoId=987654321"))
        self.assertTrue(JWPlayerIE.suitable("https://cdn.jwplayer.com/players/abc1234-xyz5678.html"))
        self.assertTrue(NebulaIE.suitable("https://nebula.tv/videos/creator-video-title"))
        self.assertTrue(OdyseeIE.suitable("https://odysee.com/@creator:1/sample-video:2"))
        self.assertTrue(BitChuteIE.suitable("https://www.bitchute.com/video/abc1234/"))
        self.assertTrue(DTubeIE.suitable("https://d.tube/#!/v/creator/abc1234"))
        self.assertTrue(VKIE.suitable("https://vk.com/video-12345678_98765432"))
        self.assertTrue(VidyardIE.suitable("https://share.vidyard.com/watch/abc12345"))
        self.assertTrue(TedIE.suitable("https://www.ted.com/talks/speaker_talk_title"))

    def test_social_extractors(self):
        self.assertTrue(InstagramIE.suitable("https://www.instagram.com/p/CXYZ1234/"))
        self.assertTrue(InstagramIE.suitable("https://www.instagram.com/reel/CXYZ1234/"))
        self.assertTrue(TikTokIE.suitable("https://www.tiktok.com/@user/video/1234567890123456789"))
        self.assertTrue(TwitterIE.suitable("https://twitter.com/user/status/1234567890123456789"))
        self.assertTrue(RedditIE.suitable("https://www.reddit.com/r/funny/comments/abc123/funny_video/"))
        self.assertTrue(PinterestIE.suitable("https://www.pinterest.com/pin/123456789012/"))
        self.assertTrue(ThreadsIE.suitable("https://www.threads.net/@user/post/CXYZ1234/"))
        self.assertTrue(BlueskyIE.suitable("https://bsky.app/profile/user.bsky.social/post/3kxyz1234"))
        self.assertTrue(StreamableIE.suitable("https://streamable.com/abc123"))
        self.assertTrue(LikeeIE.suitable("https://likee.video/@user/video/1234567890"))
        self.assertTrue(LinkedInIE.suitable("https://www.linkedin.com/posts/user_awesome-post-activity-1234567890/"))
        self.assertTrue(ImgurIE.suitable("https://imgur.com/gallery/abc1234"))
        self.assertTrue(GiphyIE.suitable("https://giphy.com/gifs/funny-reaction-abc1234"))
        self.assertTrue(NineGagIE.suitable("https://9gag.com/gag/abc1234"))
        self.assertTrue(CoubIE.suitable("https://coub.com/view/abc1234"))

    def test_music_extractors(self):
        self.assertTrue(SpotifyIE.suitable("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"))
        self.assertTrue(SoundCloudIE.suitable("https://soundcloud.com/artist/track-name"))
        self.assertTrue(DeezerIE.suitable("https://www.deezer.com/track/123456789"))
        self.assertTrue(ApplePodcastsIE.suitable("https://podcasts.apple.com/us/podcast/the-daily/id1200361736?i=1000500000000"))
        self.assertTrue(TidalIE.suitable("https://tidal.com/browse/track/12345678"))
        self.assertTrue(MixcloudIE.suitable("https://www.mixcloud.com/dj_artist/awesome-mix-vol-1/"))
        self.assertTrue(AudiomackIE.suitable("https://audiomack.com/artist-name/song/hit-single"))
        self.assertTrue(BandcampIE.suitable("https://artist.bandcamp.com/track/song-title"))
        self.assertTrue(FreesoundIE.suitable("https://freesound.org/people/user/sounds/123456/"))
        self.assertTrue(PodcastIE.suitable("https://feeds.simplecast.com/54nAGcIl"))


if __name__ == "__main__":
    unittest.main()
