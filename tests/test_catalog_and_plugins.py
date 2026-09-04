import unittest
from pydlp.extractor.catalog import UniversalCatalogIE
from pydlp.extractor.sites_db import get_all_supported_domains_count, get_platform_catalog
from pydlp.plugins.hanime_plugin import HanimePluginIE
from pydlp.core.plugins import get_custom_extractors


class TestCatalogAndPlugins(unittest.TestCase):
    def test_domain_catalog_count(self):
        count = get_all_supported_domains_count()
        self.assertGreaterEqual(count, 2000)
        catalog = get_platform_catalog()
        self.assertIn("youtube", catalog)
        self.assertIn("spotify", catalog)
        self.assertIn("bbc_iplayer", catalog)
        self.assertIn("arte", catalog)

    def test_universal_catalog_matching(self):
        self.assertTrue(UniversalCatalogIE.suitable("https://example.com/video/12345"))
        self.assertTrue(UniversalCatalogIE.suitable("https://custom-streaming-domain.org/watch?v=abc"))

    def test_hanime_plugin(self):
        self.assertTrue(HanimePluginIE.suitable("https://hanime.tv/videos/hentai/sample-show-ep-1"))
        self.assertIn(HanimePluginIE, get_custom_extractors())


if __name__ == "__main__":
    unittest.main()
