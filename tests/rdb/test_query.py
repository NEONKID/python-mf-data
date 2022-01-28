import pytest
from pymfdata.rdb.connection import AsyncSQLAlchemy, SyncSQLAlchemy

from tests.rdb.domain.query_model import MemoQuery
from tests.rdb.domain.usecase import AsyncMemoUseCaseUnitOfWork, MemoUseCaseUnitOfWork, MemoUseCase


class TestRdbQuery:
    @pytest.fixture(autouse=True)
    def setup(self, test_db_connection: SyncSQLAlchemy, test_async_db_connection: AsyncSQLAlchemy) -> None:
        self.sync_uow = MemoUseCaseUnitOfWork(test_db_connection._engine)
        self.uow = AsyncMemoUseCaseUnitOfWork(test_async_db_connection._engine)
        self.uc = MemoUseCase(self.uow)

    @pytest.mark.asyncio
    async def test_fetch_all(self):
        async with self.uow:
            result = await self.uow.query_repository.fetch_all()
            assert result is not None
            assert result != []

            for r in result:
                assert isinstance(r, MemoQuery)

    @pytest.mark.asyncio
    async def test_fetch_by_id(self):
        async with self.uow:
            result = await self.uow.query_repository.fetch_by_id(1)
            assert result is not None
            assert result.id == 1

            assert isinstance(result, MemoQuery)
