****************************
Mopidy-LeftAsRain
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-LeftAsRain.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-LeftAsRain/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-LeftAsRain.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-LeftAsRain/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/naglis/mopidy-leftasrain/master.png?style=flat
    :target: https://travis-ci.org/naglis/mopidy-leftasrain
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/naglis/mopidy-leftasrain/master.svg?style=flat
   :target: https://coveralls.io/r/naglis/mopidy-leftasrain?branch=master
   :alt: Test coverage

Mopidy extension to get tracks from `leftasrain.com <http://leftasrain.com/>`_

Installation
============

Install by running::

    pip install Mopidy-LeftAsRain


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-LeftAsRain to your Mopidy configuration file::

    [leftasrain]
    enabled = true
    db_filename = $XDG_CACHE_DIR/mopidy/leftasrain.json

To make use of this extenstion, it is recommended to first run::

    mopidy leftasrain pull

to pull all leftasrain.com songs to a local database (note: this might take a
while).


Project resources
=================

- `Source code <https://github.com/naglis/mopidy-leftasrain>`_
- `Issue tracker <https://github.com/naglis/mopidy-leftasrain/issues>`_
- `Download development snapshot <https://github.com/naglis/mopidy-leftasrain/archive/master.tar.gz#egg=Mopidy-LeftAsRain-dev>`_


Changelog
=========

v0.0.1 (2014-06-24)
----------------------------------------

- Initial release.
- Basic search capabilities.
