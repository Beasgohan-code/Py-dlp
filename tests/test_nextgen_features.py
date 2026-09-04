"""Unit tests for next-generation features: Deduplication, ASCII preview, Stems, Highlights, NFO export."""

import os
import tempfile
import unittest
from pathlib import Path

from pydlp.core.ascii_preview import TerminalMediaPreview
from pydlp.core.dedup import FuzzyDedupManager
from pydlp.core.types import MediaInfo
from pydlp.postprocessor.highlights import HighlightReelPostProcessor
from pydlp.postprocessor.plex_nfo import MediaServerNfoPostProcessor
from pydlp.postprocessor.stem_separator import AudioStemSeparatorPostProcessor


class TestNextGenFeatures(unittest.TestCase):
    """Test suite verifying next-gen AI, DSP, deduplication, and media server features."""

    def test_ascii_preview_generator(self):
        preview = TerminalMediaPreview.generate_synthetic_preview("Test Video Title", "MUSIC", width=40, height=10)
        self.assertIn("PREVIEW", preview)
        self.assertIn("Test Video Title", preview)
        self.assertIn("\033[", preview)  # Contains ANSI color sequences

    def test_fuzzy_dedup_manager(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_dedup.db"
            dedup = FuzzyDedupManager(db_path=str(db_file), similarity_threshold=0.80)

            video1 = MediaInfo(
                id="yt_123",
                extractor="youtube",
                title="Rick Astley - Never Gonna Give You Up (Official Music Video) [4K]",
                duration=212.0,
                uploader="RickAstleyVEVO",
                webpage_url="https://youtube.com/watch?v=yt_123",
            )
            dedup.record_media(video1)

            # Exact duplicate check
            is_dup, reason = dedup.is_duplicate(video1)
            self.assertTrue(is_dup)
            self.assertIn("Exact ID", reason)

            # Mirror on another platform / re-uploaded with different ID and slight title change
            video2 = MediaInfo(
                id="vimeo_999",
                extractor="vimeo",
                title="Never Gonna Give You Up - Rick Astley Official Video",
                duration=213.0,  # Within ±2.5s
                uploader="MirrorChannel",
                webpage_url="https://vimeo.com/999",
            )
            is_dup2, reason2 = dedup.is_duplicate(video2)
            self.assertTrue(is_dup2)
            self.assertIn("Fuzzy duplicate detected", reason2)

            # Completely different video
            video3 = MediaInfo(
                id="daily_456",
                extractor="dailymotion",
                title="Cooking Masterclass: How to make Italian Pizza",
                duration=600.0,
                uploader="ChefMario",
                webpage_url="https://dailymotion.com/video/456",
            )
            is_dup3, _ = dedup.is_duplicate(video3)
            self.assertFalse(is_dup3)

    def test_media_server_nfo_postprocessor(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_file = Path(tmp_dir) / "SampleMovie.mp4"
            video_file.write_bytes(b"dummy video data")

            info = MediaInfo(
                id="mov_1",
                title="Sample Movie 2026",
                description="A thrilling sci-fi adventure in deep space.",
                duration=7200.0,
                upload_date="20260904",
                uploader="SciFi Studios",
                categories=["Sci-Fi", "Adventure"],
                tags=["space", "future", "ai"],
                filepath=str(video_file),
            )

            pp = MediaServerNfoPostProcessor(options={"export_plex": True})
            self.assertTrue(pp.is_needed)

            files_del, res_info = pp.run(info)
            self.assertEqual(files_del, [])

            nfo_file = Path(tmp_dir) / "SampleMovie.nfo"
            self.assertTrue(nfo_file.exists())
            nfo_text = nfo_file.read_text(encoding="utf-8")
            self.assertIn("<movie>", nfo_text)
            self.assertIn("<title>Sample Movie 2026</title>", nfo_text)
            self.assertIn("<studio>SciFi Studios</studio>", nfo_text)
            self.assertIn("<genre>Sci-Fi</genre>", nfo_text)

    def test_stem_separator_postprocessor_config(self):
        pp = AudioStemSeparatorPostProcessor(options={"split_audio_stems": True})
        self.assertTrue(pp.is_needed)

    def test_highlight_reel_postprocessor_config(self):
        pp = HighlightReelPostProcessor(options={"auto_highlights": True, "highlight_duration": 45.0})
        self.assertTrue(pp.is_needed)


if __name__ == "__main__":
    unittest.main()
