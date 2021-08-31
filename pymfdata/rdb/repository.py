from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import AsyncIterator, Callable, final, Generic, Iterator, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from pymfdata.rdb.connection import Base
from pymfdata.common.errors import NotFoundException

MT = TypeVar("MT", bound=Base)


class AsyncRepository(ABC, Generic[MT]):
    def __init__(self, model: MT, session_factory: Callable[..., AbstractAsyncContextManager]) -> None:
        self.model = model
        self._session_factory = session_factory

    @abstractmethod
    async def find_by_pk(self, pk) -> MT:
        raise NotImplementedError("Required implementation")

    @final
    async def find_by_col(self, **kwargs) -> MT:
        if not await self.is_exists(**kwargs):
            raise NotFoundException()

        session: AsyncSession
        async with self._session_factory() as session:
            item = await session.execute(self._gen_stmt_for_param(**kwargs))
            return item.unique().scalars().one()

    @final
    def _gen_stmt_for_param(self, **kwargs) -> Select:
        stmt = select(self.model)
        if kwargs:
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        return stmt

    @final
    async def find_all(self, **kwargs) -> AsyncIterator[MT]:
        session: AsyncSession
        async with self._session_factory() as session:
            stmt = self._gen_stmt_for_param(**kwargs)
            result = await session.execute(stmt)

            return result.unique().scalars().fetchall()

    @final
    async def is_exists(self, **kwargs) -> bool:
        session: AsyncSession
        async with self._session_factory() as session:
            return await session.execute(self._gen_stmt_for_param(**kwargs).exists().select())

    @final
    async def save(self, item: Base):
        session: AsyncSession
        async with self._session_factory() as session:
            session.add(item)
            await session.commit()


class SyncRepository(ABC, Generic[MT]):
    def __init__(self, model: MT, session_factory: Callable[..., AbstractContextManager]) -> None:
        self.model = model
        self._session_factory = session_factory

    @abstractmethod
    def find_by_pk(self, pk) -> MT:
        raise NotImplementedError("Required implementation")

    @final
    def find_by_col(self, **kwargs) -> MT:
        if not self.is_exists(**kwargs):
            raise NotFoundException()

        with self._session_factory() as session:
            query = self._gen_query_for_param(session, **kwargs)
            return query.one()

    @final
    def _gen_query_for_param(self, session: Session, **kwargs) -> Query:
        query = session.query(self.model)
        if kwargs:
            for key, value in kwargs.items():
                query = query.filter(getattr(self.model.key) == value)
        return query

    @final
    def find_all(self, **kwargs) -> Iterator[MT]:
        session: Session
        with self._session_factory() as session:
            query = self._gen_query_for_param(session, **kwargs)
            return query.all()

    @final
    def is_exists(self, **kwargs) -> bool:
        with self._session_factory() as session:
            session: Session
            return session.query(self._gen_query_for_param(session, **kwargs).exists()).scalar()

    @final
    def save(self, item: Base):
        session: Session
        with self._session_factory() as session:
            session.add(item)
            session.commit()
