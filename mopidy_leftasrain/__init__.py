from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.0'

logger = logging.getLogger(__name__)


class LeftAsRainExtension(ext.Extension):

    dist_name = 'Mopidy-LeftAsRain'
    ext_name = 'leftasrain'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(LeftAsRainExtension, self).get_config_schema()
        schema['db_filename'] = config.Path(optional=True)
        schema['timeout'] = config.Integer(minimum=0)
        return schema

    def get_command(self):
        from .commands import LeftAsRainCommand
        return LeftAsRainCommand()

    def setup(self, registry):

        from .backend import LeftAsRainBackend
        registry.add('backend', LeftAsRainBackend)
