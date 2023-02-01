import contextlib
import enum
import sys
from typing import Any, Callable, Generic, Sequence, Type, TypeVar, Union, cast

from models.base import DatabaseModel
from sqlalchemy import delete, exists, func, select, update
from sqlalchemy.ext.asyncio import (AsyncResult, AsyncSession,
                                    AsyncSessionTransaction)
from sqlalchemy.orm import Session, joinedload, sessionmaker
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.elements import BinaryExpression

ASTERISK = '*'

SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=DatabaseModel)
ExpressionType = Union[BinaryExpression, ClauseElement, bool]


class TransactionStrategy(enum.IntEnum):
    ONE_PER_REQUEST = 1
    KEEP_ALIVE = 2


DEFAULT_STRATEGY = TransactionStrategy.ONE_PER_REQUEST


class Transaction:
    def __init__(self, session: AsyncSession, strategy: TransactionStrategy):
        self._session = session
        self._strategy = strategy
        self._current_txn: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> AsyncSessionTransaction:
        if self._current_txn is not None and \
                self._strategy == TransactionStrategy.KEEP_ALIVE:
            return self._current_txn
        self._current_txn = self._session.begin()
        await self._current_txn.start()
        return self._current_txn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None or exc_val is not None or exc_tb is not None:
            return await self._current_txn.__aexit__(exc_type, exc_val, exc_tb)
        if self._strategy == TransactionStrategy.KEEP_ALIVE:
            return None
        await self._current_txn.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self) -> None:
        await self._current_txn.__aexit__(None, None, None)  # noqa: WPS609

    def change_strategy(self, new_strategy: TransactionStrategy) -> None:
        self._strategy = new_strategy


class DatabaseService(Generic[SQLAlchemyModel]):  # noqa: WPS214
    model: Type[SQLAlchemyModel]

    def __init__(
            self,
            session_or_pool: Union[sessionmaker, AsyncSession],
            *,
            query_model: Type[SQLAlchemyModel] = None,
    ) -> None:
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool
        self.model = query_model or self.model
        self._transaction = Transaction(self._session, DEFAULT_STRATEGY)

    @contextlib.asynccontextmanager
    async def transaction(self) -> AsyncSessionTransaction:
        self._transaction.change_strategy(TransactionStrategy.KEEP_ALIVE)
        try:
            yield await self._transaction.__aenter__()  # noqa: WPS609
        except Exception as ex:
            await self._transaction.__aexit__(*sys.exc_info())  # noqa: WPS609
            raise ex
        finally:
            await self._transaction.close()
            self._transaction.change_strategy(DEFAULT_STRATEGY)

    async def _add(self, **values: Any) -> SQLAlchemyModel | None:
        async with self._transaction:
            model_to_add = self.model(**values)
            self._session.add(model_to_add)
        return model_to_add

    async def _add_many(self, *models: SQLAlchemyModel) -> None:
        async with self._transaction:
            bulk_save_func = make_proxy_bulk_save_func(instances=models)
            await self._session.run_sync(bulk_save_func)

    async def _get_all(
            self,
            *clauses: ExpressionType,
            load: Any | None = None,
            limit: int | None = None,
            offset: int | None = None
    ) -> list[SQLAlchemyModel]:
        statement = select(self.model).where(*clauses)
        if limit:
            statement = statement.limit(limit)
        if offset:
            statement = statement.offset(offset)
        if load is not None:
            statement = statement.options(joinedload(load))
        async with self._transaction:
            session_result: AsyncResult = \
                await self._session.execute(statement)
            scalars = session_result.scalars().unique().all()
        return cast(list[SQLAlchemyModel], scalars)

    async def _get_one(
            self,
            *clauses: ExpressionType,
            load: Any | None = None,
            loads: Any | None = None,
    ) -> SQLAlchemyModel | None:
        statement = select(self.model).where(*clauses)
        if load is not None:
            statement = statement.options(joinedload(load))
        if loads is not None:
            for _ in loads:
                statement = statement.options(joinedload(_))

        async with self._transaction:
            session_result: AsyncResult = \
                await self._session.execute(statement)
            first_scalar_result = session_result.scalars().first()
        return first_scalar_result  # type: ignore

    async def _update(self,
                      *clauses: ExpressionType,
                      **values: Any) -> None:
        statement = update(self.model).where(*clauses).values(**values)
        async with self._transaction:
            await self._session.execute(statement)

    async def _exists(self, *clauses: ExpressionType) -> bool:
        statement = exists(self.model).where(*clauses).select()
        async with self._transaction:
            session_result = (await self._session.execute(statement)).scalar()
        return cast(bool, session_result)

    async def _delete(self, *clauses: ExpressionType) -> list[SQLAlchemyModel]:
        statement = delete(self.model).where(*clauses).returning(ASTERISK)
        async with self._transaction:
            session_result = (await self._session.execute(statement)). \
                scalars().all()
        return cast(list[SQLAlchemyModel], session_result)

    async def _count(self, *clauses: ExpressionType) -> int:
        async with self._transaction:
            statement = select(func.count(ASTERISK)). \
                select_from(self.model).where(*clauses)
            async_result: AsyncResult = await self._session.execute(statement)
        return cast(int, async_result.scalar())


def make_proxy_bulk_save_func(
        instances: Sequence[Any],
        return_defaults: bool = False,
        update_changed_only: bool = True,
        preserve_order: bool = True,
) -> Callable[[Session], None]:
    def _proxy(session: Session) -> None:
        return session.bulk_save_objects(
            instances,
            return_defaults=return_defaults,
            update_changed_only=update_changed_only,
            preserve_order=preserve_order,
        )  # type: ignore

    return _proxy
