import logging

from motor.motor_asyncio import AsyncIOMotorClient

from sfg_catalog.common.singleton import SingletonMeta
from sfg_catalog.settings import MOTOR_DB, MOTOR_MAX_POOL_SIZE, MOTOR_URI

log = logging.getLogger(__name__)


class Mongo(metaclass=SingletonMeta):

    def __init__(self):
        self._client = None

    def initialize(self, loop):
        if self._client:
            return self._client

        log.info(
            'Connection to the mongodb: '
            '{uri} with pool size: {max_pool_size}'.format(
                uri=MOTOR_URI,
                max_pool_size=MOTOR_MAX_POOL_SIZE
            )
        )

        self._client = AsyncIOMotorClient(
            MOTOR_URI,
            maxPoolSize=MOTOR_MAX_POOL_SIZE,
            io_loop=loop
        )

        log.info('Default mongodb database: {}'.format(self.db.name))

    @property
    def db(self):
        try:
            return self._client.get_database(MOTOR_DB)
        except Exception as e:
            raise Exception(
                'You must define `MOTOR_URI=mongodb://host:port/database_name`'
                ' on settings, error:{}'.format(e)
            )

    def close(self):
        log.info('Closing mongodb connection')
        if self._client:
            self._client.close()
            self._client = None
