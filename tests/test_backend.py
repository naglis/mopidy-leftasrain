# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from mopidy_leftasrain.backend import track_from_song_data
from mopidy_leftasrain.remote import COVER_URL, SONG_URL


class TestTrackFromSongData(unittest.TestCase):

    def setUp(self, *args, **kwargs):
        super(TestTrackFromSongData, self).setUp(*args, **kwargs)
        self.data = {
            'id': '1',
            'url': 'test_uri',
            'artist': 'a',
            'track_name': 'b',
            'cover': 'test_cover',
            'comment': 'cover_test',
            'date': '',
            'last_modified': 0,
        }

    def test_remote_url_true_forms_correct_url(self):
        t = track_from_song_data(self.data, remote_url=True)
        self.assertEqual(t.uri, SONG_URL + 'test_uri.mp3')

    def test_remote_url_false_forms_correct_url(self):
        t = track_from_song_data(self.data, remote_url=False)
        self.assertEqual(t.uri, 'leftasrain:track:a - b.1')

    def test_cover_url(self):
        t = track_from_song_data(self.data)
        self.assertEqual(len(t.album.images), 1)
        self.assertIn(COVER_URL.format(**self.data), t.album.images)
