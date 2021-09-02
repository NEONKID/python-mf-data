from abc import ABC
from bson import ObjectId
from typing import final, List, Optional

from pymfdata.mongodb.connection import AsyncMotor


class AsyncRepository(ABC):
    def __init__(self, collection_name: str, motor: AsyncMotor) -> None:
        self._collection = motor.client[motor.db_name][collection_name]

    @final
    async def delete_by_id(self, item_id: str) -> bool:
        row = await self._collection.delete_one({"_id": ObjectId(item_id)})
        if not row:
            return False

        return True

    @final
    async def find_all(self) -> List[dict]:
        cursor = self._collection.find()
        results = list(map(lambda item: item, await cursor.to_list(length=100)))

        return results

    @final
    async def find_by_id(self, item_id: str) -> Optional[dict]:
        row = await self._collection.find_one({"_id": ObjectId(item_id)})
        if not row:
            return None

        return row

    @final
    async def save(self, req: dict) -> dict:
        return await self._collection.insert_one(req)

    @final
    async def update_by_id(self, item_id: str, req: dict) -> dict:
        await self._collection.update_one({"_id": ObjectId(item_id)}, req)
        return await self.find_by_id(item_id)
