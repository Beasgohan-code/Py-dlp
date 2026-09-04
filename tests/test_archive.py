"""Tests for DownloadArchive deduplication."""

import os
import shutil
import tempfile
import unittest
from pydlp.core.archive import DownloadArchive
from pydlp.core.types import MediaInfo


class TestDownloadArchive(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.archive_file = os.path.join(self.test_dir, "archive.txt")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_archive_record_and_contains(self):
        archive = DownloadArchive(self.archive_file)
        info = MediaInfo(id="video123", title="Test Video", extractor="youtube", extractor_key="Youtube")

        self.assertFalse(archive.contains(info))
        archive.record(info)
        self.assertTrue(archive.contains(info))

        # Reload from disk
        archive2 = DownloadArchive(self.archive_file)
        self.assertTrue(archive2.contains(info))


if __name__ == "__main__":
    unittest.main()
