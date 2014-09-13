# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urlparse

from . import logger
from .remote import LeftAsRain

import pykka
from mopidy import backend
from mopidy.models import SearchResult


class LeftAsRainBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(LeftAsRainBackend, self).__init__()
        self.config = config
        self.leftasrain = LeftAsRain(config['leftasrain']['timeout'],
                                     config['leftasrain']['db_filename'])
        self.library = LeftAsRainLibraryProvider(backend=self)
        self.uri_schemes = ['leftasrain']


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
        if uri == 'leftasrain:all':
            logger.info('Looking up all leftasrain tracks')
            result = self.backend.leftasrain.tracks_from_filter(
                lambda x: True, remote_url=True)
        elif uri.startswith('leftasrain:last:'):
            try:
                total = self.backend.leftasrain.total
                n = max([1, total - int(uri.rpartition(':')[2])])
                result = [
                    self.backend.leftasrain.track_from_id(id_, remote_url=True)
                    for id_ in xrange(n, total)]
            except ValueError as e:
                logger.exception(str(e))
                result = []
        else:
            try:
                self.backend.leftasrain.validate_lookup_uri(uri)
                id_ = uri.split('.')[-1]
                logger.info('Looking up leftasrain track with ID: %s' % id_)
                result = [
                    self.backend.leftasrain.track_from_id(id_,
                                                          remote_url=True)
                ]
            except ValueError as e:
                logger.exception(str(e))
                result = []

        self.backend.leftasrain.maybe_save()
        return result

    def search(self, query=None, uris=None):
        filters = []

        def make_filter(types, queries):
            def f(t):
                return self._filter(types, queries, t)
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
        f = lambda t: any([f_(t) for f_ in filters])

        return SearchResult(
            uri='leftasrain:search',
            tracks=self.backend.leftasrain.tracks_from_filter(f)
        )
