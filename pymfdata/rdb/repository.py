from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import AsyncIterator, Callable, final, Iterator, Protocol, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from pymfdata.rdb.connection import Base
from pymfdata.common.errors import NotFoundException

_MT = TypeVar("_MT", bound=Base)


class AsyncRepository(Protocol[_MT]):
    _model: _MT
    _session_factory: Callable[..., AbstractAsyncContextManager]
    _pk_column: str

    async def delete_by_pk(self, pk):
        if not await self.is_exists(**{self._pk_column: pk}):
            raise NotFoundException()

        item = await self.find_by_pk(pk)

        session: AsyncSession
        async with self._session_factory() as session:
            await session.delete(item)
            await session.commit()

    async def find_by_pk(self, pk) -> _MT:
        return await self.find_by_col(**{self._pk_column: pk})

    @final
    async def find_by_col(self, **kwargs) -> _MT:
        if not await self.is_exists(**kwargs):
            raise NotFoundException()

        session: AsyncSession
        async with self._session_factory() as session:
            item = await session.execute(self._gen_stmt_for_param(**kwargs))
            return item.unique().scalars().one()

    @final
    def _gen_stmt_for_param(self, **kwargs) -> Select:
        stmt = select(self._model)
        if kwargs:
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self._model, key) == value)
        return stmt

    @final
    async def find_all(self, **kwargs) -> AsyncIterator[_MT]:
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
            await session.refresh(item)

    async def update_by_pk(self, pk, req: dict):
        if not await self.is_exists(**{self._pk_column: pk}):
            raise NotFoundException()

        item = await self.find_by_pk(pk)

        session: AsyncSession
        async with self._session_factory() as session:
            for k, v in req.items():
                if v is not None:
                    setattr(item, k, v)

            await session.commit()
            await session.refresh(item)


class SyncRepository(Protocol[_MT]):
    _model: _MT
    _session_factory: Callable[..., AbstractContextManager]
    _pk_column: str

    def find_by_pk(self, pk) -> _MT:
        return self.find_by_col(**{self._pk_column: pk})

    @final
    def find_by_col(self, **kwargs) -> _MT:
        if not self.is_exists(**kwargs):
            raise NotFoundException()

        with self._session_factory() as session:
            query = self._gen_query_for_param(session, **kwargs)
            return query.one()

    @final
    def _gen_query_for_param(self, session: Session, **kwargs) -> Query:
        query = session.query(self._model)
        if kwargs:
            for key, value in kwargs.items():
                query = query.filter(getattr(self._model, key) == value)
        return query

    @final
    def find_all(self, **kwargs) -> Iterator[_MT]:
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
