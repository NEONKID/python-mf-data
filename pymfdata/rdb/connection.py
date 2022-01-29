from asyncio import current_task
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterable, Callable, Union, Optional

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from pymfdata.rdb.mapper import Base


class AsyncSQLAlchemy:
    def __init__(self, db_uri: str) -> None:
        self._db_uri = db_uri
        self._engine: Optional[AsyncEngine] = None
        self._session_factory = None

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def connect(self, **kwargs):
        self._engine = create_async_engine(self._db_uri, **kwargs)

    async def disconnect(self):
        await self._engine.dispose()

    def init_session_factory(self, autocommit: bool = False, autoflush: bool = False):
        self._session_factory = async_scoped_session(
            sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=self._engine, class_=AsyncSession),
            scopefunc=current_task)

    @asynccontextmanager
    async def session(self) -> Callable[..., AsyncSession]:
        assert self._session_factory is not None

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_db_session(self) -> Callable[..., AsyncSession]:
        assert self._session_factory is not None

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self):
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self):
        assert self._session_factory is not None
        return self._session_factory


class SyncSQLAlchemy:
    def __init__(self, db_uri: str) -> None:
        self._db_uri = db_uri
        self._engine: Union[Engine, None] = None
        self._session_factory = None

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    def connect(self, **kwargs):
        self._engine = create_engine(self._db_uri, **kwargs)

    def disconnect(self):
        self._engine.dispose()

    def init_session_factory(self, autocommit: bool = False, autoflush: bool = False):
        self._session_factory = scoped_session(sessionmaker(autocommit=autocommit,
                                                            autoflush=autoflush, bind=self._engine))

    @contextmanager
    def session(self) -> Callable[..., Session]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @property
    def session_factory(self):
        assert self._session_factory is not None
        return self._session_factory
