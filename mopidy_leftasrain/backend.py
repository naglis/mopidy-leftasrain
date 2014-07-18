# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urlparse

from mopidy import backend
from mopidy.models import SearchResult

import pykka

from . import logger
from .remote import LeftAsRain


class LeftAsRainBackend(pykka.ThreadingActor, backend.Backend):

    def __init__(self, config, audio):
        super(LeftAsRainBackend, self).__init__()
        self.config = config
        self.leftasrain = LeftAsRain(config["leftasrain"]["timeout"],
                                     config["leftasrain"]["db_filename"])
        self.library = LeftAsRainLibraryProvider(backend=self)
        self.uri_schemes = ["leftasrain"]


class LeftAsRainLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(LeftAsRainLibraryProvider, self).__init__(backend)
        self.backend.leftasrain.load_db()

    def _filter(self, types, queries, track):
        return any([q.lower() in track.get(t, "").lower() for q in queries for t in types])

    def lookup(self, uri):
        if urlparse.urlsplit(uri).scheme not in self.backend.uri_schemes:
            return []

        if uri == "leftasrain:all":
            logger.info("Looking up all leftasrain tracks")
            return self.backend.leftasrain.tracks_from_filter(lambda x: True,
                                                              remote_url=True)
        elif uri.startswith("leftasrain:last:"):
            try:
                total = self.backend.leftasrain.total
                n = max([1, total - int(uri.rpartition(":")[2])])
                return [
                    self.backend.leftasrain.track_from_id(id_, remote_url=True)
                    for id_ in xrange(n, total)]
            except ValueError as e:
                logger.exception(str(e))
                return []
        else:
            try:
                self.backend.leftasrain.validate_lookup_uri(uri)
                id_ = uri.split(".")[-1]
                logger.info("Looking up leftasrain track with ID: %s" % id_)
                return [self.backend.leftasrain.track_from_id(id_,
                                                              remote_url=True)]
            except ValueError as e:
                logger.exception(str(e))
                return []

    def search(self, query=None, uris=None):
        filters = []

        if query:
            if "any" in query:
                filters.append(lambda t: self._filter(["artist", "album", "track_name"],
                                                      query.get("any", []), t))
            if "artist" in query:
                filters.append(lambda t: self._filter(["artist"],
                                                      query.get("artist", []), t))
            if "album" in query:
                filters.append(lambda t: self._filter(["album"],
                                                      query.get("album", []), t))
            if "track_name" in query:
                filters.append(lambda t: self._filter(["track_name"],
                                                      query.get("track_name", []), t))

        # build one filter from a list of filters
        f = lambda t: any([f_(t) for f_ in filters])

        return SearchResult(uri="leftasrain:search",
                            tracks=self.backend.leftasrain.tracks_from_filter(f))
