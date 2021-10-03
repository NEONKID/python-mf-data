from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Callable, Protocol


class AbstractAsyncUnitOfWork(Protocol):
    _session_factory: Callable[..., AsyncSession]

    async def __aenter__(self):
        self._session = self._session_factory()

    async def __aexit__(self, exc_type, exc_val, traceback):
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def flush(self):
        await self._session.flush()

    async def refresh(self, item):
        await self._session.refresh(item)

    async def rollback(self):
        await self._session.rollback()


class AbstractSyncUnitOfWork(Protocol):
    _session_factory: Callable[..., Session]

    def __enter__(self):
        self._session = self._session_factory()

    def __exit__(self, exc_type, exc_val, traceback):
        self._session.close()

    def commit(self):
        self._session.commit()

    def flush(self):
        self._session.flush()

    def rollback(self):
        self._session.rollback()
