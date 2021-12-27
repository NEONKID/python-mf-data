from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from typing import Optional, Type

from pymfdata.common.command import AsyncBaseUnitOfWork, SyncBaseUnitOfWork


class AsyncSQLAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self.session = AsyncSession(self._engine)

    async def __aexit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()

    async def refresh(self, item):
        await self.session.refresh(item)

    async def rollback(self):
        await self.session.rollback()


class SyncSQLAlchemyUnitOfWork(SyncBaseUnitOfWork):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = Session(self.engine)

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        self.session.close()

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()

    def rollback(self):
        self.session.rollback()
