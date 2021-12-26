# Python Micro Framework Data

Python Micro Framework Data makes database connections easier in microframeworks like ```Falcon``` and ```FastAPI```.

This library is created with the motive of Spring Data Common, and the relational database is implemented based on ```SQLAlchemy```



Currently, this library is **still under development**. The only stable database, **SQLAlchemy**, is the relational database, and we plan to implement it so that it can be used separately according to synchronous and asynchronous processing.



<br />



## How to install (rdb)

pymfdata can use the extra option to specify which database to use. When using this library for relational database connection, use the command below.

```python
$ pip install pymfdata[rdb]
```

Or if you are using poetry, use the following command

```python
$ poetry add "pymfdata[rdb]"
```



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
