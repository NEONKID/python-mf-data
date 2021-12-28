# Python Micro Framework Data

* [한국어](https://github.com/NEONKID/python-mf-data/blob/main/README.ko.md)



<br />



Python Micro Framework Data makes database connections easier in microframeworks like [Falcon](https://falcon.readthedocs.io/en/stable/) and [FastAPI](https://fastapi.tiangolo.com/).

This library is created with the motive of [Spring Data Commons](https://docs.spring.io/spring-data/commons/docs/current/reference/html/), and the relational database is implemented based on [SQLAlchemy](https://www.sqlalchemy.org/)



Currently, this library is **still under development**. The only stable database, **SQLAlchemy**, is the relational database, and we plan to implement it so that it can be used separately according to synchronous and asynchronous processing.



<br />



## How to install (rdb)

If you are installing the Python Micro Framework Data library for a relational database, enter the command below.

```shell
$ pip install python-mf-data[rdb]
```

```shell
$ poetry add "python-mf-data[rdb]"
```

You must enter **rdb** in the extra option to install sub-dependencies such as SQLAlchemy.



<br />



## Connection Example (rdb)

If you want to create a connection in SQLAlchemy using ```pymfdata```, please follow the instructions below.

```python
from pymfdata.rdb.connection import AsyncSQLAlchemy

connection = AsyncSQLAlchemy(db_uri='postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
    'postgres', 'postgres', '127.0.0.1', '5432', 'test'))
```

```python
from pymfdata.rdb.connection import SyncSQLAlchemy

connection = SyncSQLAlchemy(db_uri='postgresql+psycopg2://{}:{}@{}:{}/{}'.format(
    'postgres', 'postgres', '127.0.0.1', '5432', 'test'))
```

When creating a connection, make sure that the application you are developing supports asynchronous processing, and then use the correct one.

(This code is an example of connecting **PostgreSQL** Dialect. If you want to use a different database dialect, enter the connection address for their dependency.)

* MySQL (https://docs.sqlalchemy.org/en/14/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql)
* Oracle (https://docs.sqlalchemy.org/en/14/dialects/oracle.html)
* PostgreSQL (https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
* Microsoft SQL Server (https://docs.sqlalchemy.org/en/14/dialects/mssql.html)
* SQLite (https://docs.sqlalchemy.org/en/14/dialects/sqlite.html)

You can specify options for connection pool settings such as connection pool size and recycling as shown below.

```python
await connection.connect(pool_size=5, pool_recycle=3600)
```

```python
connection.connect(pool_size=5, pool_recycle=3600)
```

When using a connection resource, you must call the ```connect()``` method.



<br />



## Session Factory Example (rdb)

If you want to allocate and use DB Session right away, initialize session_factory using the code below.

```python
connection.init_session_factory()
```

```init_session_factory()``` is allocated **per thread and task by default**. In the case of the synchronous method, each thread is given a unique session, and in the case of the asynchronous method, each task is given a unique session. This is using the ```scoped_session()``` method provided by ```SQLAlchemy``` and their unit of work pattern.

```python
async with connection.session() as session:
    stmt = "SELECT * from test"
    result = await session.execute(stmt)
```

```python
with connection.session() as session:
    stmt = "SELECT * from test"
    result = session.execute(stmt)
```

The initialized ```session_factory``` can be used by assigning a ```session``` using the Python context manager.



<br />



## Repository Example (rdb)

When using the repository pattern, it is used after entering the data type of the pre-defined entity model and primary key as generic arguments.

```python
from pymfdata.rdb.connection import Base
from sqlalchemy import BigInteger, Column, String, Text
from typing import Union


class MemoEntity(Base):
    __tablename__ = 'memo'
    
    id: Union[int, Column] = Column(BigInteger, primary_key=True, autoincrement=True)
    title: Union[str, Column] = Column(String(128), nullable=True)
    content: Union[str, Column] = Column(Text, nullable=True)
```

ORM models can be created using SQLAlchemy's ``declarative_base`` and contain variables already defined in pymfdata.

```python
from pymfdata.rdb.repository import AsyncRepository, AsyncSession
from typing import Optional


class MemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]):
        self._session = session
        
    async def find_by_title(title: str) -> MemoEntity:
        # Todo: define session code
```

When using the Repository protocol provided by pymfdata, the following basic methods are provided.

* ```delete(entity_model)``` : This method receives the orm model as an argument and deletes a row from the database.

* ```find_by_pk(pk)``` : This method receives the primary key as an argument and returns the entity corresponding to the key. 

  (:= ```find_by_id``` in **Spring Data JPA**)

* ```find_by_col(**kwargs)``` : A method that uses a column name as an argument key and returns an entity whose value exists in that column when the value is inserted.

* ```find_all(**kwargs)``` : A method that uses a column name as an argument key and returns all entities that have a value in that column when the value is inserted. (:=  find_all in **Spring Data JPA**)

* ```is_exists(**kwargs)``` : A method that uses a column name as an argument key and returns whether the row exists when the value is inserted.

* ```create(entity_model)``` : This method receives the orm model as an argument and add a row from the database.

* ```update(entity_model, req_dict)``` : A method that receives an ORM model and a dictionary as arguments and modifies the ORM model with the data received as a dictionary

In addition to the methods provided by default in pymfdata, you can also create and use methods as in the code above. 

Since the repository of ```pymfdata``` uses the Python [Protocol](https://www.python.org/dev/peps/pep-0544/#using-protocols), it can be used like a Java interface by implementing a separate Protocol.

```python
from pymfdata.rdb.repository import AsyncRepository, AsyncSession
from pymfdata.rdb.transaction import async_transactional
from typing import Optional


class MemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]):
        self._session = session
        
    @async_transactional(read_only=True)
    async def find_by_title(title: str) -> MemoEntity:
        # Todo: Implement the session code, but omit the session begin and commit code.
```

Additionally, it provides a way to reduce duplicated code in a session by using the ```transactional``` decorator. The ```transactional``` decorator is divided into asynchronous and synchronous, and must be used according to the implemented connection.



<br />



## Unit Of Work Example (rdb)

SQLAlchemy uses the unit of work pattern by default, but if you want to define your own unit of work, you can use this library to define it.

```python
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from pymfdata.common.usecase import BaseUseCase
from pymfdata.rdb.usecase import AsyncSQLAlchemyUnitOfWork, SyncSQLAlchemyUnitOfWork
from pymfdata.rdb.transaction import async_transactional


class AsyncMemoUseCaseUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def __aenter__(self):
        await super().__aenter__()

        self.memo_repository: MemoRepository = MemoRepository(self.session)


class MemoUseCase(BaseUseCase):
    def __init__(self, uow: AsyncMemoUseCaseUnitOfWork) -> None:
        self._uow = uow

    @async_transactional(read_only=True)
    async def find_by_id(self, item_id: int):
        return await self.uow.memo_repository.find_by_pk(item_id)
```

The unit of work pattern is also divided into asynchronous and synchronous classes, and it must be used according to the connection.

The created unit of work class can be used in the class containing business logic, and we define them as **UseCase**. This class contains the business logic of the application.

When using the unit of work pattern, use the transactional decorator on business logic methods to handle transaction processing.

(If you are using ```transactional``` decorators, please use the ```BaseUseCase``` class provided by pymfdata.)



<br />



## FastAPI Example

If you want to actively use pymfdata in FastAPI, please refer to this example.

https://github.com/NEONKID/python-mf-data-example

