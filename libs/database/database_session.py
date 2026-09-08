from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


class DatabaseSessionManager:
    def __init__(self, database_url: str, debug: bool = False) -> None:
        is_sqlite = database_url.startswith("sqlite")
        self.engine = create_async_engine(
            database_url,
            echo=debug,
            connect_args={"check_same_thread": False} if is_sqlite else {},
            poolclass=NullPool if is_sqlite else None,
            **({} if is_sqlite else {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}),
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as database_session:
            try:
                yield database_session
                await database_session.commit()
            except Exception:
                await database_session.rollback()
                raise

    async def dispose(self) -> None:
        await self.engine.dispose()


async def get_database_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    database_session_manager: DatabaseSessionManager = request.app.state.database_session_manager
    async for database_session in database_session_manager.get_session():
        yield database_session
