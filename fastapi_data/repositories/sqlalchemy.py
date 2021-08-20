from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import Callable, final, Iterator, Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from fastapi_data.connections.sqlalchemy import Base
from fastapi_data.errors import NotFoundException

ModelType = TypeVar("ModelType", bound=Base)


class AsyncRepository(ABC):
    def __init__(self, model: Type[ModelType], session_factory: Callable[..., AbstractAsyncContextManager]) -> None:
        self.model = model
        self._session_factory = session_factory

    @abstractmethod
    async def find_by_pk(self, pk) -> Type[ModelType]:
        raise NotImplementedError("Required implementation")

    @final
    async def find_by_col(self, **kwargs) -> Type[ModelType]:
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
    async def find_all(self, **kwargs) -> Iterator[Type[ModelType]]:
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


class SyncRepository(ABC):
    def __init__(self, model: Type[ModelType], session_factory: Callable[..., AbstractContextManager]) -> None:
        self.model = model
        self._session_factory = session_factory

    @abstractmethod
    def find_by_pk(self, pk) -> Type[ModelType]:
        raise NotImplementedError("Required implementation")

    @final
    def find_by_col(self, **kwargs) -> Type[ModelType]:
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
    def find_all(self, **kwargs) -> Iterator[Type[ModelType]]:
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
