"""Unit tests for massive extractors expansion and new advanced features."""

import os
import unittest
from unittest.mock import MagicMock, patch

from pydlp.core.swarm import SwarmClusterManager, SwarmNode
from pydlp.core.types import MediaInfo
from pydlp.extractor import find_extractor_for_url, list_extractors
from pydlp.extractor.booru_art import ArtStationIE, DanbooruIE, PixivIE
from pydlp.extractor.cams_premium import BongacamsIE, StripchatIE
from pydlp.extractor.doujin_manga import NHentaiIE
from pydlp.extractor.fast_tv import PlutoTVIE, TubiTVIE
from pydlp.extractor.ott_asian import HotstarIE, JioCinemaIE, SonyLivIE, Zee5IE
from pydlp.extractor.podcasts_extra import AnchorFmIE, MediumIE, SubstackIE
from pydlp.postprocessor.audio_dsp import AudioDSPPostProcessor
from pydlp.postprocessor.cloud_uploader import CloudUploaderPostProcessor
from pydlp.postprocessor.whisper_subtitles import AISubtitleGeneratorPostProcessor


class TestMassiveExpansion(unittest.TestCase):
    """Tests for Asian OTT, Fast TV, Manga/Doujin, Boorus, Cams, Podcasts, Cloud Uploader, DSP, and Swarm."""

    def test_extractor_count(self):
        extractors = list_extractors()
        # Should now be 140+ native extractors
        self.assertGreaterEqual(len(extractors), 140)

    def test_asian_ott_extractors(self):
        mock_http = MagicMock()
        mock_http.get.return_value.text.return_value = "<html><title>Test Title</title></html>"

        jio = JioCinemaIE(mock_http)
        self.assertTrue(jio.suitable("https://www.jiocinema.com/movies/sample-movie/1234567"))

        hotstar = HotstarIE(mock_http)
        self.assertTrue(hotstar.suitable("https://www.hotstar.com/in/movies/sample-film/1234567890"))

        sonyliv = SonyLivIE(mock_http)
        self.assertTrue(sonyliv.suitable("https://www.sonyliv.com/shows/sample-show/1000234567"))

        zee5 = Zee5IE(mock_http)
        self.assertTrue(zee5.suitable("https://www.zee5.com/movies/details/sample/0-0-12345"))

    def test_fast_tv_extractors(self):
        mock_http = MagicMock()
        mock_http.get.return_value.text.return_value = "<html></html>"

        tubi = TubiTVIE(mock_http)
        self.assertTrue(tubi.suitable("https://tubitv.com/movies/123456"))

        pluto = PlutoTVIE(mock_http)
        self.assertTrue(pluto.suitable("https://pluto.tv/on-demand/movies/sample-movie-123"))

    def test_doujin_and_art_extractors(self):
        mock_http = MagicMock()
        mock_http.get.return_value.text.return_value = "<html></html>"
        mock_http.get.return_value.json.return_value = {"title": {"english": "Test Manga"}, "num_pages": 24}

        nhentai = NHentaiIE(mock_http)
        self.assertTrue(nhentai.suitable("https://nhentai.net/g/123456/"))

        danbooru = DanbooruIE(mock_http)
        self.assertTrue(danbooru.suitable("https://danbooru.donmai.us/posts/1234567"))

        pixiv = PixivIE(mock_http)
        self.assertTrue(pixiv.suitable("https://www.pixiv.net/artworks/12345678"))

    def test_cams_and_podcasts_extractors(self):
        mock_http = MagicMock()
        mock_http.get.return_value.text.return_value = "<html></html>"

        stripchat = StripchatIE(mock_http)
        self.assertTrue(stripchat.suitable("https://stripchat.com/sample_model"))

        substack = SubstackIE(mock_http)
        self.assertTrue(substack.suitable("https://newsletter.substack.com/p/sample-post"))

        anchor = AnchorFmIE(mock_http)
        self.assertTrue(anchor.suitable("https://anchor.fm/show/episodes/sample-ep-123"))

    def test_cloud_uploader_postprocessor(self):
        opts = {"upload_s3": "https://s3.amazonaws.com/my-bucket"}
        uploader = CloudUploaderPostProcessor(opts)
        self.assertTrue(uploader.is_needed)

        info = MediaInfo(id="123", title="Test", filepath="/nonexistent/file.mp4")
        files_del, res_info = uploader.run(info)
        self.assertEqual(files_del, [])
        self.assertEqual(res_info.id, "123")

    def test_audio_dsp_postprocessor(self):
        opts = {"vocal_removal": True, "audio_bass_boost": 6.0}
        dsp = AudioDSPPostProcessor(opts)
        self.assertTrue(dsp.is_needed)

    def test_ai_subtitle_generator_postprocessor(self):
        opts = {"ai_transcribe": True, "ai_transcribe_model": "tiny"}
        sub_gen = AISubtitleGeneratorPostProcessor(opts)
        self.assertTrue(sub_gen.is_needed)

    def test_swarm_cluster_manager(self):
        cluster = SwarmClusterManager("http://node1:8000,http://node2:8000")
        self.assertTrue(cluster.has_active_nodes)
        self.assertEqual(len(cluster.nodes), 2)
        self.assertEqual(cluster.nodes[0].endpoint_url, "http://node1:8000")


if __name__ == "__main__":
    unittest.main()
