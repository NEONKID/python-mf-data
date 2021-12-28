import pytest
from pymfdata.rdb.connection import AsyncSQLAlchemy, SyncSQLAlchemy

from tests.rdb.domain.dto import MemoRequest
from tests.rdb.domain.entity import MemoEntity
from tests.rdb.domain.usecase import AsyncMemoUseCaseUnitOfWork, MemoUseCaseUnitOfWork, MemoUseCase


class TestRdb:
    @pytest.fixture(autouse=True)
    def setup(self, test_db_connection: SyncSQLAlchemy, test_async_db_connection: AsyncSQLAlchemy) -> None:
        self.sync_uow = MemoUseCaseUnitOfWork(test_db_connection._engine)
        self.uow = AsyncMemoUseCaseUnitOfWork(test_async_db_connection._engine)
        self.uc = MemoUseCase(self.uow)

    @pytest.mark.asyncio
    async def test_insert_for_async_uow(self):
        req = {
            'content': 'Sample Async Data'
        }

        async with self.uow:
            entity = MemoEntity(**req)
            self.uow.memo_repository.create(entity)
            await self.uow.commit()

    def test_sync_uow(self):
        req = {
            'content': 'Sample Sync Data'
        }

        with self.sync_uow:
            entity = MemoEntity(**req)
            self.sync_uow.memo_repository.create(entity)
            self.sync_uow.commit()

    @pytest.mark.asyncio
    async def test_find_for_transactional(self):
        item = await self.uc.find_by_id(1)
        assert item is not None

    @pytest.mark.asyncio
    async def test_write_for_transactional(self):
        req = MemoRequest(content="Practice Memo")

        item = await self.uc.create_memo(req)
        assert item.id is not None
