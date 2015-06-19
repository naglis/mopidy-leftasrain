# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urlparse

from mopidy import backend
from mopidy.models import Album, Artist, SearchResult, Track

import pykka

from . import logger
from .remote import COVER_URL, LeftAsRain, SONG_URL


def track_from_song_data(data, remote_url=False):
    if remote_url:
        uri = urlparse.urljoin(SONG_URL, '%s.mp3' % data['url'])
    else:
        uri = 'leftasrain:track:{artist:s} - {track_name:s}.{id:s}'.format(
            **data)

    return Track(
        name=data['track_name'],
        artists=[Artist(name=data['artist'])],
        album=Album(name='leftasrain.com',
                    images=[COVER_URL.format(**data)]),
        comment=data['comment'].replace('\n', ''),
        date=data['date'],
        track_no=int(data['id']),
        last_modified=data['last_modified'],
        uri=uri
    )


class LeftAsRainBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['leftasrain']

    def __init__(self, config, audio):
        super(LeftAsRainBackend, self).__init__()
        self.audio = audio
        self.config = config
        self.leftasrain = LeftAsRain(config['leftasrain']['timeout'],
                                     config['leftasrain']['db_filename'])
        self.playback = LeftAsRainPlaybackProvider(audio=audio, backend=self)
        self.library = LeftAsRainLibraryProvider(backend=self)


class LeftAsRainPlaybackProvider(backend.PlaybackProvider):

    def translate_uri(self, uri):
        id_ = uri.split('.')[-1]
        song_data = self.backend.leftasrain.song_from_id(id_)
        if song_data:
            track = track_from_song_data(song_data, remote_url=True)
            return track.uri


class LeftAsRainLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(LeftAsRainLibraryProvider, self).__init__(backend)
        self.backend.leftasrain.load_db()

    def _filter(self, types, queries, track):
        return any([
            q.lower() in track.get(t, '').lower()
            for q in queries for t in types
        ])

    def lookup(self, uri):
        if urlparse.urlsplit(uri).scheme not in self.backend.uri_schemes:
            return []

        result = []
        song_from_id = self.backend.leftasrain.song_from_id
        if uri == 'leftasrain:all':
            logger.info('Looking up all leftasrain tracks')
            result = [
                track_from_song_data(s, remote_url=True)
                for s in self.backend.leftasrain.songs]
        elif uri.startswith('leftasrain:last:'):
            try:
                total = self.backend.leftasrain.total
                n = max([1, total - int(uri.rpartition(':')[2])])
                result = [
                    track_from_song_data(song_from_id(id_), remote_url=True)
                    for id_ in xrange(n, total)]
            except ValueError as e:
                logger.exception(e)
                result = []
        else:
            try:
                self.backend.leftasrain.validate_lookup_uri(uri)
                id_ = uri.split('.')[-1]
                logger.info('Looking up leftasrain track with ID: %s', id_)
                result = [
                    track_from_song_data(song_from_id(id_), remote_url=True)
                ]
            except ValueError as e:
                logger.exception(e)
                result = []

        self.backend.leftasrain.maybe_save()
        return result

    def search(self, query=None, uris=None, exact=False):
        # TODO Support exact search

        filters = []

        def make_filter(types, queries):
            def f(t):
                return self._filter(types, queries, t)
            return f

        def make_or_filter(filters):
            def f(t):
                return any([f_(t) for f_ in filters])
            return f

        if query:
            if 'any' in query:
                filters.append(make_filter(['artist', 'album', 'track_name'],
                                           query.get('any', [])))
            if 'artist' in query:
                filters.append(make_filter(['artist'],
                                           query.get('artist', [])))
            if 'album' in query:
                filters.append(make_filter(['album'], query.get('album', [])))
            if 'track_name' in query:
                filters.append(make_filter(['track_name'],
                                           query.get('track_name', [])))

        # build one filter from a list of filters
        f = make_or_filter(filters)

        return SearchResult(
            uri='leftasrain:search',
            tracks=map(track_from_song_data,
                       filter(f, self.backend.leftasrain.songs))
        )
