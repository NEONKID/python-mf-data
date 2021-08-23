from abc import ABC
from bson import ObjectId
from typing import final

from py_mf_data.connections.motor import AsyncMotor
from py_mf_data.errors import NotFoundException


class AsyncRepository(ABC):
    def __init__(self, collection_name: str, motor: AsyncMotor) -> None:
        self._collection = motor.client[motor.db_name][collection_name]

    @final
    async def delete_by_id(self, item_id: str):
        row = await self._collection.delete_one({"_id": ObjectId(item_id)})
        if not row:
            raise NotFoundException()

    @final
    async def find_all(self):
        cursor = self._collection.find()
        results = list(map(lambda item: item, await cursor.to_list(length=100)))

        return results

    @final
    async def find_by_id(self, item_id: str):
        row = await self._collection.find_one({"_id": ObjectId(item_id)})
        if not row:
            raise NotFoundException()

        return row

    @final
    async def save(self, req: dict):
        return await self._collection.insert_one(req)

    @final
    async def update_by_id(self, item_id: str, req: dict):
        await self._collection.update_one({"_id": ObjectId(item_id)}, req)
        return await self.find_by_id(item_id)
