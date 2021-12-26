from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from pymfdata.rdb.command import AsyncSQLAlchemyUnitOfWork, SyncSQLAlchemyUnitOfWork

from tests.rdb.domain.dto import MemoRequest
from tests.rdb.domain.repository import AsyncMemoRepository, SyncMemoRepository


class AsyncMemoUseCaseUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def __aenter__(self):
        await super().__aenter__()

        self._memo_repository: AsyncMemoRepository = AsyncMemoRepository(self._session)


class MemoUseCaseUnitOfWork(SyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    def __enter__(self):
        super().__enter__()

        self._memo_repository: SyncMemoRepository = SyncMemoRepository(self._session)
