from motor.motor_asyncio import AsyncIOMotorClient
from typing import Union


class AsyncMotor:
    def __init__(self, db_name, db_uri: str) -> None:
        self._db_uri = db_uri
        self.db_name = db_name
        self.client: Union[AsyncIOMotorClient, None] = None

    async def connect(self):
        self.client = AsyncIOMotorClient(self._db_uri)

    async def disconnect(self):
        self.client.close()
