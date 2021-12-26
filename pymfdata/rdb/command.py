from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from typing import Optional, Type

from common.command import AsyncBaseUnitOfWork, SyncBaseUnitOfWork


class AsyncSQLAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self._session = AsyncSession(self._engine)

    async def __aexit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def flush(self):
        await self._session.flush()

    async def refresh(self, item):
        await self._session.refresh(item)

    async def rollback(self):
        await self._session.rollback()


class SyncSQLAlchemyUnitOfWork(SyncBaseUnitOfWork):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._session: Optional[Session] = None

    def __enter__(self):
        self._session = Session(self._engine)

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        self._session.close()

    def commit(self):
        self._session.commit()

    def flush(self):
        self._session.flush()

    def rollback(self):
        self._session.rollback()
