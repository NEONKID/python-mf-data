from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from typing import Optional, Type

from pymfdata.common.usecase import AsyncBaseUnitOfWork, SyncBaseUnitOfWork


class AsyncSQLAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._session: Optional[AsyncSession] = None

    @property
    def engine(self) -> AsyncEngine:
        assert self._engine is not None
        return self._engine

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None
        return self._session

    async def __aenter__(self):
        self._session = AsyncSession(self.engine)

    async def __aexit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        await super().__aexit__(exc_type, exc_val, traceback)
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
        self._engine = engine
        self._session: Optional[Session] = None

    @property
    def engine(self) -> Engine:
        assert self._engine is not None
        return self._engine

    @property
    def session(self) -> Session:
        assert self._session is not None
        return self._session

    def __enter__(self):
        self._session = Session(self.engine)

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        super().__exit__(exc_type, exc_val, traceback)
        self.session.close()

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()

    def rollback(self):
        self.session.rollback()
