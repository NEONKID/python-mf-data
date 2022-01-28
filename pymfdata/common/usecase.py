from abc import ABC, abstractmethod
from typing import final, Optional, Protocol, Type, TypeVar, Union


class AsyncBaseUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError("required __aenter__ call for UoW Pattern")

    async def __aexit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        if exc_type:
            await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError("Choice ORM commit func")

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError("Choice ORM rollback func")


class SyncBaseUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> None:
        raise NotImplementedError("required __enter__ call for UoW Pattern")

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_val: Optional[Exception], traceback):
        if exc_type:
            self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError("Choice ORM commit func")

    @abstractmethod
    def rollback(self):
        raise NotImplementedError("Choice ORM rollback func")


_UT = TypeVar("_UT", bound=Union[AsyncBaseUnitOfWork, SyncBaseUnitOfWork])


class BaseUseCase(Protocol[_UT]):
    _uow: _UT

    @property
    def uow(self) -> _UT:
        assert self._uow is not None
        return self._uow
