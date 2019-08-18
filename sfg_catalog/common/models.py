import logging

from attrdict import AttrDict
from bson import ObjectId

from sfg_catalog.common.mongo import Mongo

log = logging.getLogger(__name__)


class BaseModel(AttrDict):
    schema = None
    collection_name = None

    def __init__(self, **kwargs):
        if self.schema:
            kwargs = self.schema.validate(kwargs)
        super().__init__(**kwargs)

    def to_dict(self):
        return self.__getstate__()[0]

    @classmethod
    def _get_db(cls):
        cls.mongo = Mongo()
        return cls.mongo.db

    @classmethod
    def _get_collection(cls):
        if not cls.collection_name:
            raise TypeError('You must define `colection_name`')

        return getattr(cls._get_db(), cls.collection_name)

    async def _insert(self):
        log.info('Save new document in collection "{}"'.format(
            self.collection_name
        ))

        result = await self._get_collection().insert_one(
            self.to_dict(),
        )
        self['_id'] = result.inserted_id

    async def _update(self):
        if not isinstance(self['_id'], ObjectId):
            self['_id'] = ObjectId(self['_id'])

        log.info('Edit document "{}" in collection "{}"'.format(
            str(self['_id']), self.collection_name
        ))
        model_dict = self.to_dict()
        del model_dict['_id']

        await self._get_collection().update_one(
            {'_id': self['_id']}, {'$set': model_dict}, upsert=False
        )

    async def save(self):
        if '_id' in self:
            await self._update()
        else:
            await self._insert()

    async def delete(self):
        if not isinstance(self['_id'], ObjectId):
            self['_id'] = ObjectId(self['_id'])

        log.warn('Remove document "{}" from collection "{}"'.format(
            str(self['_id']), self.collection_name
        ))
        await self._get_collection().delete_one({'_id': self['_id']})

    @classmethod
    async def get(cls, **kwargs):
        result = await cls._get_collection().find_one(kwargs)
        if result:
            return cls(**result)

    @classmethod
    async def list(cls, query=None, skip=0, limit=0):
        cursor = cls._get_collection().find(
            query or {}, limit=limit, skip=skip
        )

        result = []

        while await cursor.fetch_next:
            result.append(cls(**cursor.next_object()))

        return result

    @classmethod
    async def _create_or_update(cls, id, model_dict):
        await cls._get_collection().update_one(
            {'id': id}, {'$set': model_dict}, upsert=True
        )

    @classmethod
    async def count(cls, query={}):
        return await cls._get_collection().count_documents(query)
