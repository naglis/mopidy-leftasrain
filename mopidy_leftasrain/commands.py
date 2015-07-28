from mopidy import commands

from . import logger
from .remote import LeftAsRain


class LeftAsRainCommand(commands.Command):
    help = 'Help for leftasrain command'

    def __init__(self):
        super(LeftAsRainCommand, self).__init__()
        self.add_child('pull', LeftAsRainPullCommand())


class LeftAsRainPullCommand(commands.Command):
    help = 'Pull full leftasrain.com playlist to a local database'

    def __init__(self):
        super(LeftAsRainPullCommand, self).__init__()

    def run(self, args, config):
        logger.info('Hit Ctrl^C to cancel at anytime')

        leftasrain = LeftAsRain(config['leftasrain']['timeout'],
                                config['leftasrain']['db_filename'])
        leftasrain.load_db()
        count = len(leftasrain.songs)
        logger.info('%d songs already in leftasrain DB.' % count)

        logger.info('There are a total of %d songs on leftasrain.com' %
                    leftasrain.total)

        try:
            for id_ in range(1, leftasrain.total):
                if str(id_) in leftasrain.ids:
                    continue

                leftasrain.song_from_id(id_)

                diff = leftasrain.total - len(leftasrain.songs)
                if diff % 50 == 0:
                    logger.info('%d songs remaining' % diff)
        except KeyboardInterrupt:
            logger.info('Aborted by user')
        finally:
            logger.info('Saving DB...')
            leftasrain.save_db()
