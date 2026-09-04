"""Tests for newly added extractors (Spotify, Rumble, Pinterest, Threads, Bluesky, Streamable)."""

import unittest
from pydlp.extractor.bluesky import BlueskyIE
from pydlp.extractor.pinterest import PinterestIE
from pydlp.extractor.rumble import RumbleIE
from pydlp.extractor.spotify import SpotifyIE
from pydlp.extractor.streamable import StreamableIE
from pydlp.extractor.threads import ThreadsIE


class TestNewExtractors(unittest.TestCase):
    def test_spotify_matching(self):
        self.assertTrue(SpotifyIE.suitable("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"))
        self.assertTrue(SpotifyIE.suitable("https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3"))
        self.assertTrue(SpotifyIE.suitable("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"))

    def test_rumble_matching(self):
        self.assertTrue(RumbleIE.suitable("https://rumble.com/v12345a-awesome-video.html"))
        self.assertTrue(RumbleIE.suitable("https://rumble.com/embed/v12345a"))

    def test_pinterest_matching(self):
        self.assertTrue(PinterestIE.suitable("https://www.pinterest.com/pin/123456789012345678/"))

    def test_threads_matching(self):
        self.assertTrue(ThreadsIE.suitable("https://www.threads.net/@user/post/C1234567890"))

    def test_bluesky_matching(self):
        self.assertTrue(BlueskyIE.suitable("https://bsky.app/profile/alice.bsky.social/post/3kz4m5n6o7p"))

    def test_streamable_matching(self):
        self.assertTrue(StreamableIE.suitable("https://streamable.com/abc1234"))


if __name__ == "__main__":
    unittest.main()
