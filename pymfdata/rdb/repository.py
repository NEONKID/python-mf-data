from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Callable, final, Iterator, get_args, List, Protocol, Optional, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from pymfdata.rdb.connection import Base

_MT = TypeVar("_MT", bound=Base)    # Model Type
_T = TypeVar("_T")                  # Primary key Type


class AsyncRepository(Protocol[_MT, _T]):
    _session_factory: Callable[..., AbstractAsyncContextManager]

    @property
    def _model(self):
        return get_args(self.__orig_bases__[0])[0]

    @property
    def _pk_column(self) -> str:
        return inspect(self._model).primary_key[0].name

    async def delete_by_pk(self, pk: _T) -> bool:
        session: AsyncSession
        async with self._session_factory() as session:
            item = await self.find_by_pk(session, pk)
            if item is not None:
                await session.delete(item)
                await session.commit()

                return True

            return False

    async def find_by_pk(self, session: AsyncSession, pk: _T) -> Optional[_MT]:
        return await self.find_by_col(session, **{self._pk_column: pk})

    @final
    async def find_by_col(self, session: AsyncSession, **kwargs) -> Optional[_MT]:
        item = await session.execute(self._gen_stmt_for_param(**kwargs))
        return item.unique().scalars().one_or_none()

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
            result = await session.execute(self._gen_stmt_for_param(**kwargs).exists().select())
            return result.scalar()

    @final
    async def save(self, item: _MT):
        session: AsyncSession
        async with self._session_factory() as session:
            session.add(item)
            await session.commit()
            await session.refresh(item)

    async def update_by_pk(self, pk: _T, req: dict) -> bool:
        session: AsyncSession
        async with self._session_factory() as session:
            item = await self.find_by_pk(session, pk)
            if item is not None:
                for k, v in req.items():
                    if v is not None:
                        setattr(item, k, v)

                await session.commit()
                await session.refresh(item)

                return True
            return False


class SyncRepository(Protocol[_MT, _T]):
    _session_factory: Callable[..., AbstractContextManager]

    @property
    def _model(self):
        return get_args(self.__orig_bases__[0])[0]

    @property
    def _pk_column(self) -> str:
        return inspect(self._model).primary_key[0].name

    @final
    def count(self, **kwargs) -> int:
        return self._gen_query_for_param(**kwargs).count()

    def delete_by_pk(self, pk: _T) -> bool:
        session: Session
        with self._session_factory() as session:
            item = self.find_by_pk(session, pk)
            if item is not None:
                session.delete(item)
                session.commit()

                return True
            return False

    def find_by_pk(self, session: Session, pk: _T) -> Optional[_MT]:
        return self.find_by_col(session, **{self._pk_column: pk})

    @final
    def find_by_col(self, session: Session, **kwargs) -> Optional[_MT]:
        query = self._gen_query_for_param(session, **kwargs)
        return query.one_or_none()

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
        session: Session
        with self._session_factory() as session:
            item = self.find_by_pk(session, pk)
            if item is not None:
                for k, v in req.items():
                    if v is not None:
                        setattr(item, k, v)

                session.commit()
                session.refresh(item)

                return True
            return False
