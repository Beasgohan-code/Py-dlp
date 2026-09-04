"""Unit tests for yt-dlp parity, config files, match filters, embedding, and completions."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pydlp.core.completion import generate_completion_script
from pydlp.core.config import ConfigFileParser
from pydlp.core.match_filter import MatchFilter
from pydlp.core.types import MediaFormat, MediaInfo
from pydlp.core.updater import SelfUpdater
from pydlp.postprocessor.embedder import MediaEmbedderPostProcessor


class TestParityAndPower(unittest.TestCase):
    """Test suite for power features, updater, match filter, embedder, and completions."""

    def test_config_file_parsing(self):
        sample_conf = """
        # Py-dlp Configuration
        --limit-rate 5M
        -P /tmp/downloads
        --no-warnings
        --format "bestvideo+bestaudio"
        """
        with tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False) as f:
            f.write(sample_conf)
            conf_path = f.name

        try:
            args = ConfigFileParser.load_config_args(custom_path=conf_path)
            self.assertIn("--limit-rate", args)
            self.assertIn("5M", args)
            self.assertIn("-P", args)
            self.assertIn("/tmp/downloads", args)
            self.assertIn("--no-warnings", args)
        finally:
            if os.path.exists(conf_path):
                os.remove(conf_path)

    def test_match_filter_expressions(self):
        info_pass = MediaInfo(
            id="v1",
            title="Passing Video",
            duration=120,
            view_count=5000,
            upload_date="20260515",
            is_live=False,
            formats=[MediaFormat(format_id="1", url="http://example.com", filesize=20 * 1024 * 1024)],
        )

        # Match expression
        filter1 = MatchFilter(match_filter_str="duration > 60 & view_count >= 1000 & !is_live")
        res1, reason1 = filter1.matches(info_pass)
        self.assertTrue(res1)
        self.assertIsNone(reason1)

        # Fail expression
        filter2 = MatchFilter(match_filter_str="duration > 300")
        res2, reason2 = filter2.matches(info_pass)
        self.assertFalse(res2)
        self.assertIsNotNone(reason2)

        # Date filter
        filter_date = MatchFilter(dateafter="20260101", datebefore="20260901")
        res3, _ = filter_date.matches(info_pass)
        self.assertTrue(res3)

        filter_date_fail = MatchFilter(dateafter="20260601")
        res4, _ = filter_date_fail.matches(info_pass)
        self.assertFalse(res4)

    def test_media_embedder_postprocessor(self):
        opts = {
            "embed_subs": True,
            "embed_thumbnail": True,
            "embed_metadata": True,
            "embed_chapters": True,
        }
        embedder = MediaEmbedderPostProcessor(opts)
        self.assertTrue(embedder.is_needed)

        info = MediaInfo(id="123", title="Test Embed", filepath="/tmp/nonexistent.mp4")
        files_del, res_info = embedder.run(info)
        self.assertEqual(files_del, [])
        self.assertEqual(res_info.id, "123")

    def test_completion_scripts(self):
        bash_script = generate_completion_script("bash")
        self.assertIn("_pydlp_completion", bash_script)
        self.assertIn("complete -F _pydlp_completion pydlp", bash_script)

        zsh_script = generate_completion_script("zsh")
        self.assertIn("#compdef pydlp py-dlp", zsh_script)

        fish_script = generate_completion_script("fish")
        self.assertIn("complete -c pydlp", fish_script)

    def test_self_updater_mock(self):
        updater = SelfUpdater(color=False)
        with patch.object(updater, "check_for_updates", return_value=(False, "2026.09.04")):
            ret = updater.update()
            self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
