from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database


class AsyncPyMongo:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    def __init__(self, db_name, db_uri: str) -> None:
        self._db_uri = db_uri
        self.db = db_name

    """
    :param minPoolSize: Minimum Pool Size
    :param maxPoolSize: Maximum Pool size   (Default: 100)
    """
    async def connect(self, **kwargs):
        self.client = AsyncIOMotorClient(self._db_uri, **kwargs)

    async def disconnect(self):
        self.client.close()


class SyncPyMongo:
    client: MongoClient = None
    db: Database = None

    def __init__(self, db_name, db_uri: str) -> None:
        self._db_uri = db_uri
        self.db = db_name

    """
    :param minPoolSize: Minimum Pool Size
    :param maxPoolSize: Maximum Pool Size   (Default: 100)
    """
    def connect(self, **kwargs):
        self.client = MongoClient(self._db_uri, **kwargs)

    def disconnect(self):
        self.client.close()
