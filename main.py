import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import dotenv_values

from handlers.addposts import post_router
from handlers.menu import menu_router
from handlers.editposts import edit_router
from handlers.addbot import add_router
from handlers.push import push_router
from handlers.editbot import bot_router

from database.work import DB

from middleware.db import DBMiddleware
from middleware.scheulder import SchedulerMiddleware
from middleware.process import ProcessMiddleware

from sendler.send_message import Clients


async def main():
    config = dotenv_values(".env")
    print(config['TOKEN'])
    bot = Bot(token=config['TOKEN'])

    scheduler = AsyncIOScheduler()
    scheduler.start()

    cls = Clients(bot)

    dp = Dispatcher(storage=MemoryStorage())
    db = DB()
    dp.update.middleware(DBMiddleware(session_pool=db.sessionmaker))
    dp.update.middleware(SchedulerMiddleware(scheduler=scheduler))
    dp.update.middleware(ProcessMiddleware(process=cls))
    dp.include_routers(menu_router, post_router, edit_router, add_router, push_router, bot_router)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
