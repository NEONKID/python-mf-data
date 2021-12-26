import pytest
from pymfdata.rdb.connection import AsyncSQLAlchemy, SyncSQLAlchemy

from tests.rdb.domain.entity import MemoEntity
from tests.rdb.domain.usecase import AsyncMemoUseCaseUnitOfWork, MemoUseCaseUnitOfWork


class TestRdb:
    @pytest.fixture(autouse=True)
    def setup(self, test_db_connection: SyncSQLAlchemy, test_async_db_connection: AsyncSQLAlchemy) -> None:
        self._uow = MemoUseCaseUnitOfWork(test_db_connection._engine)
        self._async_uow = AsyncMemoUseCaseUnitOfWork(test_async_db_connection._engine)

    @pytest.mark.asyncio
    async def test_insert_for_async_uow(self):
        req = {
            'content': 'Sample Async Data'
        }

        async with self._async_uow:
            entity = MemoEntity(**req)
            self._async_uow._memo_repository.create(entity)
            await self._async_uow.commit()

    def test_sync_uow(self):
        req = {
            'content': 'Sample Sync Data'
        }

        with self._uow:
            entity = MemoEntity(**req)
            self._uow._memo_repository.create(entity)
            self._uow.commit()
