from typing import final, Protocol, Union

from pymfdata.common.command import AsyncBaseUnitOfWork, SyncBaseUnitOfWork


class BaseUseCase(Protocol):
    _uow: Union[AsyncBaseUnitOfWork, SyncBaseUnitOfWork]

    @final
    @property
    def uow(self):
        assert self._uow is not None
        return self._uow
