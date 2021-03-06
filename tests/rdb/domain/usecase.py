from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from pymfdata.common.usecase import BaseUseCase
from pymfdata.rdb.usecase import AsyncSQLAlchemyUnitOfWork, SyncSQLAlchemyUnitOfWork
from pymfdata.rdb.transaction import async_transactional

from tests.rdb.domain.dto import MemoRequest
from tests.rdb.domain.entity import MemoEntity
from tests.rdb.domain.repository import (AsyncMemoRepository, AsyncMemoQueryRepository,
                                         SyncMemoRepository, SyncMemoQueryRepository)


class AsyncMemoUseCaseUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def __aenter__(self):
        await super().__aenter__()

        self.memo_repository: AsyncMemoRepository = AsyncMemoRepository(self.session)
        self.query_repository: AsyncMemoQueryRepository = AsyncMemoQueryRepository(self.session)


class MemoUseCaseUnitOfWork(SyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    def __enter__(self):
        super().__enter__()

        self.memo_repository: SyncMemoRepository = SyncMemoRepository(self.session)
        self.query_repository: SyncMemoQueryRepository = SyncMemoQueryRepository(self.session)


class MemoUseCase(BaseUseCase[AsyncMemoUseCaseUnitOfWork]):
    def __init__(self, uow: AsyncMemoUseCaseUnitOfWork) -> None:
        self._uow = uow

    @async_transactional(read_only=True)
    async def find_by_id(self, item_id: int):
        return await self.uow.memo_repository.find_by_pk(item_id)

    @async_transactional()
    async def create_memo(self, req: MemoRequest):
        entity = MemoEntity(**req.dict())

        self.uow.memo_repository.create(entity)
        return entity
