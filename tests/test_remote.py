# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from mopidy_leftasrain.remote import split_title


class TestSplitTitle(unittest.TestCase):

    def test_split_artist_title_simple(self):
        test_string = 'artist - title'
        artist, title = split_title(test_string)
        self.assertEqual(artist, 'artist')
        self.assertEqual(title, 'title')

    def test_split_artist_title_two_dashes(self):
        test_string = 'artist with dash in-name - title'
        artist, title = split_title(test_string)
        self.assertEqual(artist, 'artist with dash in-name')
        self.assertEqual(title, 'title')

    def test_split_artist_title_no_dash(self):
        test_string = 'this is only the title'
        artist, title = split_title(test_string)
        self.assertEqual(artist, 'Unknown artist')
        self.assertEqual(title, 'this is only the title')

    def test_split_artist_empty_title(self):
        test_string = ''
        artist, title = split_title(test_string)
        self.assertEqual(artist, 'Unknown artist')
        self.assertEqual(title, 'Unknown title')
