from bson import ObjectId
from typing import final, List, Optional, Protocol
from motor.core import AgnosticBaseCursor, AgnosticCollection, Cursor
from pymongo.collection import Collection

from pymfdata.mongodb.connection import AsyncPyMongo, SyncPyMongo
from pymfdata.mongodb.models import _T, _MT


class AsyncRepository(Protocol[_MT, _T]):
    _collection: AgnosticCollection

    @property
    def collection(self) -> AgnosticCollection:
        assert self._collection is not None
        return self._collection

    # def __init__(self, collection_name: str, motor: AsyncPyMongo) -> None:
    #     self._collection: AgnosticCollection = motor.client[motor.db][collection_name]

    @final
    async def delete_by_id(self, item_id: _T) -> bool:
        row = await self.collection.delete_one({"_id": item_id})
        if not row:
            return False

        return True

    @final
    async def find_all(self, **kwargs) -> List[dict]:
        cursor: AgnosticBaseCursor = self.collection.find()
        return list(map(lambda item: item, await cursor.to_list(**kwargs)))

    @final
    async def find_by_id(self, item_id: _T) -> Optional[dict]:
        row = await self.collection.find_one({"_id": item_id})
        if not row:
            return None

        return row

    @final
    async def save(self, req: _MT) -> dict:
        return await self.collection.insert_one(req.dict())

    @final
    async def update_by_id(self, item_id: _T, req: _MT):
        await self.collection.update_one({"_id": item_id}, req.dict())


class SyncRepository(Protocol[_MT, _T]):
    _collection: Collection

    @property
    def collection(self) -> Collection:
        assert self._collection is not None
        return self._collection

    @final
    def delete_by_id(self, item_id: _T) -> bool:
        row = self.collection.find_one({"_id": item_id})
        if not row:
            return False

        return True

    @final
    def find_all(self, **kwargs) -> List[dict]:
        cursor: Cursor = self.collection.find(**kwargs)
        return list(map(lambda item: item, cursor))

    @final
    def find_by_id(self, item_id: _T) -> Optional[dict]:
        row = self.collection.find_one({"_id": item_id})
        if not row:
            return None

        return row

    @final
    def save(self, req: _MT) -> _T:
        return self.collection.insert_one(req.dict()).inserted_id

    @final
    def update_by_id(self, item_id: _T, req: _MT):
        self.collection.update_one({"_id": item_id}, req.dict())
