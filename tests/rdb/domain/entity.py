from pymfdata.rdb.connection import Base
from sqlalchemy import BigInteger, Column, String
from typing import Union


class MemoEntity(Base):
    __tablename__ = 'memo'

    id: Union[int, Column] = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    content: Union[str, Column] = Column(String(128), nullable=True)
