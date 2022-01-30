import enum

from pymfdata.rdb.usecase import AsyncSession, Session
from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable


class Propagation(enum.Enum):
    REQUIRED = "required"
    REQUIRES_NEW = "requires_new"


async def __async_propagation_required(self, func, read_only: bool, session: AsyncSession, args, kwargs):
    if not session.is_active:
        session.begin(subtransactions=True)

    result = await func(self, *args, **kwargs)
    if not read_only:
        await session.commit()
        try:
            inspect(result)
            await session.refresh(result)
        except NoInspectionAvailable:
            pass

    return result


def __sync_propagation_required(self, func, read_only: bool, session: Session, args, kwargs):
    if not session.is_active:
        session.begin(subtransactions=True)

    result = func(self, *args, **kwargs)
    if not read_only:
        session.commit()

    return result


async def __async_requires_new(self, func, read_only: bool, session: AsyncSession, args, kwargs):
    if not session.is_active:
        session.begin()

    result = await func(self, *args, **kwargs)
    if not read_only:
        await session.commit()
        try:
            inspect(result)
            await session.refresh(result)
        except NoInspectionAvailable:
            pass

    return result


def __sync_requires_new(self, func, read_only: bool, session: Session, args, kwargs):
    if not session.is_active:
        session.begin()

    result = func(self, *args, **kwargs)
    if not read_only:
        session.commit()

    return result


def async_transactional(read_only: bool = False, propagation: Propagation = Propagation.REQUIRES_NEW):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            if hasattr(self, 'uow'):
                async with self.uow:
                    if propagation == Propagation.REQUIRED:
                        result = await __async_propagation_required(self=self, func=func, read_only=read_only,
                                                                    session=self.uow.session, args=args, kwargs=kwargs)
                    else:
                        result = await __async_requires_new(self=self, func=func, read_only=read_only,
                                                            session=self.uow.session, args=args, kwargs=kwargs)

                    return result

            elif hasattr(self, 'session'):
                if propagation == Propagation.REQUIRED:
                    result = await __async_propagation_required(self=self, func=func, read_only=read_only,
                                                                session=self.session, args=args, kwargs=kwargs)
                else:
                    result = await __async_requires_new(self=self, func=func, read_only=read_only,
                                                        session=self.session, args=args, kwargs=kwargs)

                return result

        return wrapper

    return decorator


def sync_transactional(read_only: bool = False, propagation: Propagation = Propagation.REQUIRES_NEW):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'uow'):
                with self.uow:
                    if propagation == Propagation.REQUIRED:
                        result = __sync_propagation_required(self=self, func=func, read_only=read_only,
                                                             session=self.uow.session, args=args, kwargs=kwargs)
                    else:
                        result = __sync_requires_new(self=self, func=func, read_only=read_only,
                                                     session=self.uow.session, args=args, kwargs=kwargs)

                    return result

            elif hasattr(self, 'session'):
                if propagation == Propagation.REQUIRED:
                    result = __sync_propagation_required(self=self, func=func, read_only=read_only,
                                                         session=self.session, args=args, kwargs=kwargs)
                else:
                    result = __sync_requires_new(self=self, func=func, read_only=read_only,
                                                 session=self.session, args=args, kwargs=kwargs)

                return result

        return wrapper

    return decorator
