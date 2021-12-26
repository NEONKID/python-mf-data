import pytest

from pymfdata.rdb.connection import AsyncSQLAlchemy, Base, SyncSQLAlchemy
from tests import event_loop


async_db = AsyncSQLAlchemy(db_uri='postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
    'postgres', 'postgres', '127.0.0.1', '5432', 'test'))

sync_db = SyncSQLAlchemy(db_uri='postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
    'postgres', 'postgres', '127.0.0.1', '5432', 'test'))


@pytest.fixture(scope="session")
async def test_async_db_connection():
    if async_db._session_factory is None:
        await async_db.connect(connect_args={"server_settings": {"application_name": "pymfdata Test Runner"}})
        async_db.init_session_factory()

        async with async_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    yield async_db

    if async_db._session_factory is not None:
        await async_db.disconnect()


@pytest.fixture(scope="session")
def test_db_connection():
    if sync_db._session_factory is None:
        sync_db.connect(connect_args={"application_name": "pymfdata Test Runner"})
        sync_db .init_session_factory()

        Base.metadata.drop_all(sync_db._engine)
        Base.metadata.create_all(sync_db._engine)

    yield sync_db

    if sync_db._session_factory is not None:
        sync_db.disconnect()
