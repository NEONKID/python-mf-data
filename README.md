# Python Micro Framework Data

Python Micro Framework Data makes database connections easier in microframeworks like ```Falcon``` and ```FastAPI```.

This library is created with the motif of Spring Data Common, and the relational database is implemented based on ```SQLAlchemy```



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



## Example (rdb)

If you want to create a connection in SQLAlchemy using ```pymfdata```, please follow the instructions below.

```python
from pymfdata.rdb.connection import AsyncSQLAlchemy

connection = AsyncSQLAlchemy(db_uri='postgresql+asyncpg://{}:{}@{}:{}/{}'.format('postgres', 'postgres', '127.0.0.1', '5432', 'test'))
```

```python
from pymfdata.rdb.connection import SyncSQLAlchemy

connection = SyncSQLAlchemy(db_uri='postgresql+psycopg2://{}:{}@{}:{}/{}'.format('postgres', 'postgres', '127.0.0.1', '5432', 'test'))
```

When creating a connection, make sure that the application you are developing supports asynchronous processing, and then use the correct one.



<br />



