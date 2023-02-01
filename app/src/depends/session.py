from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

session_factory: sessionmaker | None = None


def get_session_factory() -> sessionmaker:
    if not session_factory:
        raise NotImplementedError()
    return session_factory


async def get_session(s_factory=Depends(get_session_factory)) -> AsyncGenerator:
    session: AsyncSession = s_factory()
    try:
        yield session
    finally:
        await session.close()
