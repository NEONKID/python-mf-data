from pymfdata.rdb.repository import (AsyncRepository, BaseAsyncRepository,
                                     BaseSyncRepository, SyncRepository, AsyncSession, Session)
from sqlalchemy import select
from typing import List, Optional

from tests.rdb.domain.entity import MemoEntity
from tests.rdb.domain.query_model import MemoQuery


class AsyncMemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]) -> None:
        self._session = session


class AsyncMemoQueryRepository(BaseAsyncRepository):
    def __init__(self, session: Optional[AsyncSession]) -> None:
        self._session = session

    async def fetch_all(self) -> List[MemoQuery]:
        stmt = select(MemoQuery)

        result = await self.session.execute(stmt)
        return result.unique().scalars().fetchall()

    async def fetch_by_id(self, _id: int) -> MemoQuery:
        stmt = select(MemoQuery).where(MemoQuery.id == _id)

        result = await self.session.execute(stmt)
        return result.unique().scalars().one_or_none()


class SyncMemoRepository(SyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[Session]) -> None:
        self._session = session


class SyncMemoQueryRepository(BaseSyncRepository):
    def __init__(self, session: Optional[Session]) -> None:
        self._session = session
