from __future__ import unicode_literals

import json
import os
import socket
import time
import urllib
import urllib2

from . import logger

COVER_URL = 'http://leftasrain.com/img/covers/{cover:s}'
SONG_URL = 'http://leftasrain.com/musica/'
NEXT_TRACK_URL = 'http://leftasrain.com/getNextTrack.php?%s'

FIELD_MAPPING = {
    0: 'id',
    1: 'date',
    2: 'track_name',
    3: 'album',
    4: 'url',
    5: 'comment',
    8: 'cover',
    9: 'post',
}


def split_title(t):
    """Split (artist, title) from "artist - title" """
    artist, title = 'Unknown artist', 'Unknown title'
    if '-' not in t:
        if t:
            title = t
    else:
        try:
            values = t.split(' - ')
            artist = values[0]
            if len(values) > 2:
                title = ' - '.join(values[1:])
            else:
                title = values[1]
        except IndexError:
            title = t
    return artist, title


def map_song_data(data):
    """Map a list of song attributes to a dict with meaningful keys"""
    result = {}
    for i, v in enumerate(data):
        if i not in FIELD_MAPPING:
            continue
        field = FIELD_MAPPING[i]
        if field == 'track_name':
            a, t = split_title(v)
            result['artist'] = a
            result['track_name'] = t
        else:
            result[field] = v
    result['last_modified'] = int(time.time())

    return result


class LeftAsRain(object):

    def __init__(self, timeout, db_filename):
        self._timeout = timeout
        self._total = None
        self.db_filename = db_filename
        self._db_changed = False
        self._db = {}

    @property
    def ids(self):
        return self._db.keys()

    @property
    def songs(self):
        return self._db.values()

    @property
    def total(self):
        """Returns the total number of songs on leftasrain.com"""

        if not self._total:
            try:
                last_track = self._fetch_song(-1, use_cache=False)
                if not last_track:
                    logger.error('Unable to get total track count')
                    self._total = 0
                else:
                    self._total = int(last_track.get('id', 0)) + 1
            except Exception as e:
                logger.exception(e)
                self._total = 0

        return self._total

    def maybe_save(self):
        if self._db_changed:
            self.save_db()

    def save_db(self):
        logger.info('Saving leftasrain DB to: %s', self.db_filename)
        try:
            with open(self.db_filename, 'w') as f:
                json.dump(self._db, f, indent=4)
        except Exception as e:
            logger.exception('Error while saving: %s', e)
        else:
            self._db_changed = False

    def load_db(self):
        if os.path.exists(self.db_filename):
            logger.info('Loading leftasrain DB: %s', self.db_filename)
            with open(self.db_filename, 'r') as f:
                self._db = json.load(f)
            logger.info('%d LeftAsRain songs loaded', len(self._db))

    def _fetch_song(self, song_id, use_cache=True, max_retries=3):
        """Returns a list of song attributes"""
        attempt = 0

        if not isinstance(song_id, int):
            song_id = int(song_id)

        if use_cache and str(song_id) in self._db:
            logger.debug('leftasrain: DB hit for ID: %d', song_id)
            return self._db[str(song_id)]

        params = urllib.urlencode({'currTrackEntry': song_id + 1,
                                   'shuffle': 'false'})
        url = NEXT_TRACK_URL % params
        while attempt < max_retries:
            attempt += 1
            try:
                result = urllib2.urlopen(url, timeout=self._timeout)
                data = map_song_data(json.load(result))
                if use_cache:
                    self._db[str(song_id)] = data
                    self._db_changed = True
                return data
            except (urllib2.HTTPError, urllib2.URLError, socket.gaierror,
                    socket.timeout) as e:
                logger.exception('Fetch failed: %s', e)
            except (IOError, ValueError) as e:
                logger.exception('Fetch failed for unkown reason: %s', e)
                break  # Do not retry.
        return {}

    def validate_lookup_uri(self, uri):
        if '.' not in uri:
            raise ValueError('Wrong leftasrain URI format')
        try:
            id_ = uri.split('.')[-1]
            if not id_.isdigit():
                raise ValueError('leftasrain song ID must be a positive int')
            if int(id_) >= self.total:
                raise ValueError('No such leftasrain song with ID: %s' % id_)
        except Exception as e:
            raise ValueError('Error while validating URI: %s' % str(e))

    def song_from_id(self, id_):
        return self._fetch_song(id_)
