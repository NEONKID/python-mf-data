# Python Micro Framework Data

* [English](README.md)



<br />



Python Micro Framework Data는 [Falcon](https://falcon.readthedocs.io/en/stable/), [FastAPI](https://fastapi.tiangolo.com/)와 같은 마이크로프레임워크 계열에서 데이터베이스 연결을 쉽게 해주는 라이브러리입니다.

이 라이브러리는 [Spring Data Commons](https://docs.spring.io/spring-data/commons/docs/current/reference/html/)를 모티브로 개발하였으며 NoSQL과 관계형 데이터베이스에 대해 지원하고자 합니다. 현재, SQLAlchemy로 구현된 관계형 데이터베이스의 코드는 안정적이며 NoSQL은 현재 MongoDB부터 지원을 계획하고 있습니다.



<br />



## Connection Example (rdb)

아래의 코드는 pymfdata에 있는 SQLAlchemy의 커넥션을 생성하는 예제입니다.

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

SQLAlchemy는 비동기 커넥션을 지원합니다. 따라서 pymfdata에서도 이에 맞게 동기 커넥션과 비동기 커넥션 클래스가 나뉘어져 있으며 이에 맞게 사용할 수 있습니다. 

(위 코드는 PostgreSQL을 사용했을 때의 예제입니다. 만약, 다른 데이터베이스의 연결이 필요하다면 아래의 링크를 참고하십시오)

* MySQL (https://docs.sqlalchemy.org/en/14/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql)
* Oracle (https://docs.sqlalchemy.org/en/14/dialects/oracle.html)
* PostgreSQL (https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
* Microsoft SQL Server (https://docs.sqlalchemy.org/en/14/dialects/mssql.html)
* SQLite (https://docs.sqlalchemy.org/en/14/dialects/sqlite.html)

커넥션 풀에 대한 설정은 아래의 코드를 참고하십시오.

```python
await connection.connect(pool_size=5, pool_recycle=3600)
```

```python
connection.connect(pool_size=5, pool_recycle=3600)
```

만들어진 객체는 ```connect``` 메서드 호출 후 사용할 수 있으며, 커넥션 메서드에서 커넥션 풀의 갯수 등을 설정할 수 있습니다. 



<br />



## Session Factory Example (rdb)

SQLAlchemy에서 제공하는 DB Session 객체를 직접 사용하고자 하는 경우, 아래의 session_factory 예제 코드를 참고하십시오.

```python
connection.init_session_factory()
```

위에서 만든 커넥션 객체에서 ```init_session_factory()``` 메서드를 통해 매 요청마다 session을 만들 수 있습니다. 이 메서드는 SQLAlchemy에서 제공하는 작업 단위 패턴인 ```scoped_session()``` 및 ```async_scoped_session()```을 사용하기 때문에 **기본적으로 스레드 혹은 태스크 별로 session이 할당**됩니다. 

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

할당된 세션은 커넥션 객체의 session을 파이썬의 컨텍스트 매니저를 이용해 할당 받아 사용할 수 있습니다. 



<br />



## Repository Example (rdb)

pymfdata에서 제공하는 저장소(Repository) 패턴을 이용하기 위해서는 먼저 Entity를 생성하고 제네릭에 그 타입과 기본키 타입을 지정해줘야 합니다.

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

SQLAlchemy를 이용해 ORM 모델을 만들 때는 ```declarative_base```를 이용합니다. pymfdata에서 이미 정의된 변수가 있으므로 이를 import하여 사용할 수도 있습니다.

```python
from pymfdata.rdb.repository import AsyncRepository, AsyncSession
from typing import Optional


class MemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]):
        self._session = session
        
    async def find_by_title(title: str) -> MemoEntity:
        # Todo: define session code
```

pymfdata에서 제공하는 Repository Protocol에는 아래의 기본 메서드들이 제공됩나다.

* ```delete(entity_model)``` :  ORM 모델을 인자로 받아 데이터베이스에서 해당 모델을 제거하는 메서드

* ```find_by_pk(pk)``` : 기본키에 해당하는 ORM 모델을 반환하는 메서드 (**Spring Data JPA** 의 ```find_by_id```와 동일)

* ```find_by_col(**kwargs)``` : 컬럼 이름을 인자 키로 지정 후, 찾고자 하는 값을 넣으면 해당 컬럼의 값과 매칭되는 ORM 모델을 반환하는 메서드 (***단, 한 개만 반환***)

* ```find_all(**kwargs)``` : 컬럼 이름을 인자 키로 지정 후, 찾고자 하는 값을 넣으면 해당 컬럼의 값과 매칭되는 ORM 모델들을 반환하는 메서드. (***모든 데이터 반환***)

  (**Spring Data JPA**의 ```find_all```과 유사)

* ```is_exists(**kwargs)``` : 컬럼 이름을 인자 키로 지정 후, 찾고자하는 값을 넣으면 해당 컬럼의 값과 매칭되는 행이 있으면 ```True```, 없으면 ```False``` 반환하는 메서드.

* ```create(entity_model)``` : ORM 모델을 인자로 받아 데이터베이스에 해당 모델을 추가하는 메서드

* ```update(entity_model, req_dict)``` : ORM 모델과 딕셔너리 데이터를 인자로 받고, ORM 모델의 데이터를 업데이트하는 메서드

pymfdata에서 제공하는 기본 메서드들 외에도 구현한 Repository 클래스에 원하는 메서드를 구현할 수 있습니다.

또한 Repository 클래스는 Java의 Interface와 유사한 Python의 [Protocol](https://www.python.org/dev/peps/pep-0544/#using-protocols)로 구현되어 있어 이를 이용해 Interface처럼 구현할 수도 있습니다.

```python
from pymfdata.rdb.repository import AsyncRepository, AsyncSession
from pymfdata.rdb.transaction import async_transactional
from typing import Optional


class MemoRepository(AsyncRepository[MemoEntity, int]):
    def __init__(self, session: Optional[AsyncSession]):
        self.session = session
        
    @async_transactional(read_only=True)
    async def find_by_title(title: str) -> MemoEntity:
        # Todo: Implement the session code, but omit the session begin and commit code.
```

pymfdata에서 제공하는 session은 autocommit 옵션이 주어져 있지 않아, ```commit()``` 호출이 필요한 경우 메서드에서 ```commit()``` 메서드를 호출해야 합니다. 여기서 pymfdata의 ```transactional``` 데코레이터를 이용하면 이러한 보일러 플레이트 코드를 신경쓰지 않아도 됩니다. 

단, 커넥션의 동기, 비동기 여부에 따라서 ```async_transactional```, ```sync_transactional```을 맞춰서 사용해야 합니다.



<br />



## Unit Of Work Example (rdb)

SQLAlchemy에서 기본적으로 제공하는 작업 단위 패턴 외에 직접 작업 단위 패턴을 구현하여 사용하고자 하는 경우 이 라이브러리에서 제공하는 작업 단위 패턴을 이용해 보십시오.

```python
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from pymfdata.rdb.command import AsyncSQLAlchemyUnitOfWork, SyncSQLAlchemyUnitOfWork
from pymfdata.rdb.transaction import async_transactional


class AsyncMemoUseCaseUnitOfWork(AsyncSQLAlchemyUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        super().__init__(engine)

    async def __aenter__(self):
        await super().__aenter__()

        self.memo_repository: MemoRepository = MemoRepository(self.session)
            

class MemoUseCase:
    def __init__(self, uow: AsyncMemoUseCaseUnitOfWork) -> None:
        self.uow = uow

    @async_transactional(read_only=True)
    async def find_by_id(self, item_id: int):
        return await self.uow.memo_repository.find_by_pk(item_id)
```

작업 단위 패턴 또한 비동기, 동기에 따라 클래스가 별도로 구현되어 있습니다. 생성한 커넥션에 맞춰 사용하시면 됩니다.

이렇게 만들어진 작업 단위 클래스는 애플리케이션의 비즈니스 로직을 정의할 ***UseCase*** 클래스에 담아 사용할 수 있습니다. 사실상 비즈니스 로직에서 트랜잭션이 필요로 하는 경우의 코드이기 때문에 작업 단위 패턴에 있는 메서드에 ```transactional``` 데코레이터를 사용하여 트랜잭션을 처리할 수 있습니다.