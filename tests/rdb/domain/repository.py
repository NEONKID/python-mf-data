from pymfdata.rdb.repository import AsyncRepository, SyncRepository, AsyncSession, Session
from typing import Optional

from tests.rdb.domain.entity import MemoEntity


class AsyncMemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]) -> None:
        self._session = session


class SyncMemoRepository(SyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[Session]) -> None:
        self._session = session
