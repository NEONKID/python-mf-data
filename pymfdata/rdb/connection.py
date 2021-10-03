from asyncio import current_task
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, Callable, Iterator, Union

from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session

Base = declarative_base()


class AsyncSQLAlchemy:
    def __init__(self, db_uri: str) -> None:
        self._db_uri = db_uri
        self._engine: Union[AsyncEngine, None] = None
        self._session_factory = None

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def connect(self, autocommit: bool = False, autoflush: bool = False):
        self._engine = create_async_engine(self._db_uri, echo=True)
        self._session_factory = async_scoped_session(
            sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=self._engine, class_=AsyncSession),
            scopefunc=current_task())

    async def disconnect(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> Callable[..., AsyncSession]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

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

    def connect(self, autocommit: bool = False, autoflush: bool = False):
        self._engine = create_engine(self._db_uri, echo=True)
        self._session_factory = scoped_session(sessionmaker(autocommit=autocommit,
                                                            autoflush=autoflush, bind=self._engine))

    def disconnect(self):
        self._engine.dispose()

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
