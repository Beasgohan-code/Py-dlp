"""Tests for extractor URL matching and dispatching."""

import unittest
from pydlp.core.http import HttpClient
from pydlp.extractor import find_extractor_for_url
from pydlp.extractor.youtube import YoutubeIE, YoutubePlaylistIE, YoutubeSearchIE
from pydlp.extractor.vimeo import VimeoIE
from pydlp.extractor.tiktok import TikTokIE
from pydlp.extractor.instagram import InstagramIE
from pydlp.extractor.twitter import TwitterIE
from pydlp.extractor.reddit import RedditIE
from pydlp.extractor.twitch import TwitchIE
from pydlp.extractor.soundcloud import SoundCloudIE
from pydlp.extractor.bilibili import BilibiliIE
from pydlp.extractor.dailymotion import DailymotionIE
from pydlp.extractor.facebook import FacebookIE
from pydlp.extractor.bandcamp import BandcampIE
from pydlp.extractor.podcast import PodcastIE
from pydlp.extractor.archiveorg import ArchiveOrgIE
from pydlp.extractor.peertube import PeerTubeIE
from pydlp.extractor.generic import GenericIE


class TestExtractors(unittest.TestCase):
    def setUp(self):
        self.http = HttpClient()

    def test_youtube_matching(self):
        self.assertTrue(YoutubeIE.suitable("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(YoutubeIE.suitable("https://youtu.be/dQw4w9WgXcQ"))
        self.assertTrue(YoutubeIE.suitable("https://www.youtube.com/shorts/dQw4w9WgXcQ"))
        self.assertTrue(YoutubePlaylistIE.suitable("https://www.youtube.com/playlist?list=PL1234567890ABCDEF"))
        self.assertTrue(YoutubeSearchIE.suitable("ytsearch:python tutorial"))
        self.assertTrue(YoutubeSearchIE.suitable("ytsearch5:machine learning"))

    def test_vimeo_matching(self):
        self.assertTrue(VimeoIE.suitable("https://vimeo.com/11111111"))
        self.assertTrue(VimeoIE.suitable("https://player.vimeo.com/video/11111111"))

    def test_tiktok_matching(self):
        self.assertTrue(TikTokIE.suitable("https://www.tiktok.com/@user/video/7123456789012345678"))

    def test_instagram_matching(self):
        self.assertTrue(InstagramIE.suitable("https://www.instagram.com/reel/C123456789/"))
        self.assertTrue(InstagramIE.suitable("https://www.instagram.com/p/C123456789/"))

    def test_twitter_matching(self):
        self.assertTrue(TwitterIE.suitable("https://twitter.com/user/status/1234567890123456789"))
        self.assertTrue(TwitterIE.suitable("https://x.com/user/status/1234567890123456789"))

    def test_reddit_matching(self):
        self.assertTrue(RedditIE.suitable("https://www.reddit.com/r/funny/comments/123456/title/"))

    def test_twitch_matching(self):
        self.assertTrue(TwitchIE.suitable("https://clips.twitch.tv/GloriousSlickWombat"))
        self.assertTrue(TwitchIE.suitable("https://www.twitch.tv/videos/123456789"))

    def test_soundcloud_matching(self):
        self.assertTrue(SoundCloudIE.suitable("https://soundcloud.com/artist-name/track-name"))

    def test_bilibili_matching(self):
        self.assertTrue(BilibiliIE.suitable("https://www.bilibili.com/video/BV1xx411c7mD"))

    def test_dailymotion_matching(self):
        self.assertTrue(DailymotionIE.suitable("https://www.dailymotion.com/video/x7tgad0"))

    def test_facebook_matching(self):
        self.assertTrue(FacebookIE.suitable("https://www.facebook.com/watch/?v=123456789"))

    def test_bandcamp_matching(self):
        self.assertTrue(BandcampIE.suitable("https://artist.bandcamp.com/track/cool-song"))

    def test_podcast_matching(self):
        self.assertTrue(PodcastIE.suitable("https://feeds.simplecast.com/54nAGcIl.rss"))

    def test_archiveorg_matching(self):
        self.assertTrue(ArchiveOrgIE.suitable("https://archive.org/details/night_of_the_living_dead"))

    def test_peertube_matching(self):
        self.assertTrue(PeerTubeIE.suitable("https://peertube.tv/videos/watch/12345678-abcd-1234-abcd-1234567890ab"))

    def test_fallback_to_generic(self):
        ie = find_extractor_for_url("https://example.com/stream.mp4", self.http)
        self.assertEqual(ie.IE_NAME, "generic")


if __name__ == "__main__":
    unittest.main()
