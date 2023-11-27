import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.model import Base


class DB:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///userbot.db", echo=True)
        self.sessionmaker = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        loop = asyncio.get_running_loop()
        loop.create_task(self.add_main())

    async def add_main(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
