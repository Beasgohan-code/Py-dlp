"""Tests for dynamic plugin registration."""

import unittest
from pydlp.core.plugins import (
    get_custom_extractors,
    get_custom_postprocessors,
    register_extractor,
    register_postprocessor,
)
from pydlp.extractor.base import InfoExtractor
from pydlp.postprocessor.base import BasePostProcessor


class DummyCustomIE(InfoExtractor):
    IE_NAME = "dummy_custom"
    _VALID_URL = r"https?://custom-platform\.com/(?P<id>[0-9]+)"


class DummyCustomPP(BasePostProcessor):
    def run(self, info):
        return [], info


class TestPlugins(unittest.TestCase):
    def test_custom_registration(self):
        register_extractor(DummyCustomIE)
        self.assertIn(DummyCustomIE, get_custom_extractors())

        register_postprocessor(DummyCustomPP)
        self.assertIn(DummyCustomPP, get_custom_postprocessors())


if __name__ == "__main__":
    unittest.main()
