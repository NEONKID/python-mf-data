from typing import final, get_args, List, Protocol, Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.selectable import Select

from pymfdata.rdb.mapper import Base

_MT = TypeVar("_MT", bound=Base)    # Model Type
_T = TypeVar("_T")                  # Primary key Type


class BaseAsyncRepository(Protocol):
    _session: AsyncSession

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None
        return self._session


class AsyncRepository(BaseAsyncRepository, Protocol[_MT, _T]):
    @property
    def _model(self):
        return get_args(self.__orig_bases__[0])[0]

    @property
    def _pk_column(self) -> str:
        return inspect(self._model).primary_key[0].name

    async def delete(self, item: _MT):
        await self.session.delete(item)

    async def find_by_pk(self, pk: _T) -> Optional[_MT]:
        return await self.find_by_col(**{self._pk_column: pk})

    @final
    async def find_by_col(self, **kwargs) -> Optional[_MT]:
        item = await self.session.execute(self._gen_stmt_for_param(**kwargs))
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
        stmt = self._gen_stmt_for_param(**kwargs)
        result = await self.session.execute(stmt)

        return result.unique().scalars().fetchall()

    @final
    async def is_exists(self, **kwargs) -> bool:
        result = await self.session.execute(self._gen_stmt_for_param(**kwargs).exists().select())
        return result.scalar()

    @final
    def create(self, item: _MT):
        self.session.add(item)

    @final
    async def create_all(self, items: List[_MT]):
        self.session.add_all(items)

    def update(self, item: _MT, req: dict):
        for k, v in req.items():
            if v is not None:
                setattr(item, k, v)


class BaseSyncRepository(Protocol):
    _session: Session

    @property
    def session(self) -> Session:
        assert self._session is not None
        return self._session


class SyncRepository(BaseSyncRepository, Protocol[_MT, _T]):

    @property
    def _model(self):
        return get_args(self.__orig_bases__[0])[0]

    @property
    def _pk_column(self) -> str:
        return inspect(self._model).primary_key[0].name

    @final
    def count(self, **kwargs) -> int:
        return self._gen_query_for_param(**kwargs).count()

    def delete(self, item: _MT):
        self.session.delete(item)

    def find_by_pk(self, pk: _T) -> Optional[_MT]:
        return self.find_by_col(**{self._pk_column: pk})

    @final
    def find_by_col(self, **kwargs) -> Optional[_MT]:
        query = self._gen_query_for_param(**kwargs)
        return query.one_or_none()

    @final
    def _gen_query_for_param(self, **kwargs) -> Query:
        query = self.session.query(self._model)
        if kwargs:
            for key, value in kwargs.items():
                query = query.filter(getattr(self._model, key) == value)
        return query

    @final
    def find_all(self, **kwargs) -> List[_MT]:
        query = self._gen_query_for_param(**kwargs)
        return query.all()

    @final
    def is_exists(self, **kwargs) -> bool:
        return self.session.query(self._gen_query_for_param(**kwargs).exists()).scalar()

    @final
    def create(self, item: Base):
        self.session.add(item)

    def update(self, item: _MT, req: dict):
        for k, v in req.items():
            if v is not None:
                setattr(item, k, v)
