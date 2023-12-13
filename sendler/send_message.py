import asyncio
from typing import List
from pyrogram import Client, idle
from pyrogram.errors import FloodWait, PeerIdInvalid
from dotenv import load_dotenv

from aiogram import Bot

load_dotenv()


class Clients:
    def __init__(self, bot: Bot):
        self.clients_lis: List[Client] = []
        self.bot = bot

    async def do_send_message(self, data: dict):
        for cl in self.clients_lis:
            if cl.name == data['account']:
                try:
                    await cl.send_photo(chat_id=data['chat'], caption=data['text'],
                                        photo=open(f"photos\{data['photo']}", "rb"))
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await self.bot.send_message(chat_id=data['owner'], text=f"Ваш аккаунт {data['account']} "
                                                                            f"получил ограничение из-за флуда")
                except PeerIdInvalid:
                    await self.load_session(cl)
                    await cl.send_photo(chat_id=data['chat'], caption=data['text'], photo=data['photo'])
                except Exception as e:
                    print(e)

    async def do_add_new_client(self, name, session_string):
        try:
            client = Client(name=name, session_string=session_string)
            await client.start()
            self.clients_lis.append(client)
            await self.load_session(client)
        except Exception as e:
            print(e)

    async def load_many_clients(self, clients: list):
        for cl in clients:
            await self.do_add_new_client(cl[0], cl[1])

    @staticmethod
    async def load_session(session: Client):
        async for _ in session.get_dialogs():
            await session.storage.save()


if __name__ == '__main__':
    pass
