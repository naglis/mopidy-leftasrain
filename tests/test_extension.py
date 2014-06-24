from __future__ import unicode_literals

import unittest

from mopidy_leftasrain import LeftAsRainExtension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = LeftAsRainExtension()

        config = ext.get_default_config()

        self.assertIn('[leftasrain]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = LeftAsRainExtension()

        schema = ext.get_config_schema()

        self.assertIn('db_filename', schema)
        self.assertIn('timeout', schema)
