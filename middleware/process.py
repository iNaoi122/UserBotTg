from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from multiprocessing import Process
from aiogram.types.base import TelegramObject

from sendler.send_message import Clients


class ProcessMiddleware(BaseMiddleware):
    def __init__(self, process: Clients):
        super().__init__()
        self.process = process

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        data["process"] = self.process
        return await handler(event, data)
