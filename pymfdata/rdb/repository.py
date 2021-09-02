from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Callable, final, Iterator, List, Protocol, TypeVar, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from pymfdata.rdb.connection import Base

_MT = TypeVar("_MT", bound=Base)    # Model Type
_T = TypeVar("_T")                  # Primary key Type


class AsyncRepository(Protocol[_MT, _T]):
    _model: _MT
    _session_factory: Callable[..., AbstractAsyncContextManager]
    _pk_column: str

    async def delete_by_pk(self, pk: _T) -> bool:
        item = await self.find_by_pk(pk)
        if item is not None:
            session: AsyncSession
            async with self._session_factory() as session:
                await session.delete(item)
                await session.commit()

            return True
        return False

    async def find_by_pk(self, pk: _T) -> Optional[_MT]:
        return await self.find_by_col(**{self._pk_column: pk})

    @final
    async def find_by_col(self, **kwargs) -> Optional[_MT]:
        if not await self.is_exists(**kwargs):
            return None

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
    async def find_all(self, **kwargs) -> List[_MT]:
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

    async def update_by_pk(self, pk: _T, req: dict) -> bool:
        item = await self.find_by_pk(pk)
        if item is not None:
            session: AsyncSession
            async with self._session_factory() as session:
                for k, v in req.items():
                    if v is not None:
                        setattr(item, k, v)

                await session.commit()
                await session.refresh(item)

            return True
        return False


class SyncRepository(Protocol[_MT, _T]):
    _model: _MT
    _session_factory: Callable[..., AbstractContextManager]
    _pk_column: str

    def delete_by_pk(self, pk: _T) -> bool:
        item = self.find_by_pk(pk)
        if item is not None:
            session: Session
            with self._session_factory() as session:
                session.delete(item)
                session.commit()

            return True
        return False

    def find_by_pk(self, pk: _T) -> Optional[_MT]:
        return self.find_by_col(**{self._pk_column: pk})

    @final
    def find_by_col(self, **kwargs) -> Optional[_MT]:
        if not self.is_exists(**kwargs):
            return None

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
        session: Session
        with self._session_factory() as session:
            return session.query(self._gen_query_for_param(session, **kwargs).exists()).scalar()

    @final
    def save(self, item: Base):
        session: Session
        with self._session_factory() as session:
            session.add(item)
            session.commit()

    def update_by_pk(self, pk: _T, req: dict) -> bool:
        item = self.find_by_pk(pk)
        if item is not None:
            session: Session
            with self._session_factory() as session:
                for k, v in req.items():
                    if v is not None:
                        setattr(item, k, v)

                await session.commit()
                await session.refresh(item)

            return True
        return False
