"""Database session dependencies.

Routers depend on `get_db` / `get_analytics_db`, never on
`app.database.session` directly — that indirection is what lets tests
override the dependency with a different session factory.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_analytics_session, get_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_analytics_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_analytics_session():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]
AnalyticsDbSession = Annotated[AsyncSession, Depends(get_analytics_db)]
