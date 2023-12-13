from aiogram import types, Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, MEMBER, IS_NOT_MEMBER
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.model import Session, Chat, AllChats

from kb import keymain

menu_router = Router()


@menu_router.message(Command("start"))
async def start_hand(message: types.Message):
    await message.answer(text="Я бот для управления юзерботами в тг", reply_markup=keymain.main_keyboard())


@menu_router.callback_query(F.data == "reset")
async def reset(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(text="Я бот для управления юзерботами в тг", reply_markup=keymain.main_keyboard())


@menu_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def add_chat(event: types.ChatMemberUpdated, session: AsyncSession):
    await session.merge(AllChats(chat_id=event.chat.id))
    await session.commit()


@menu_router.callback_query(F.data == "stop")
async def stop(call: types.CallbackQuery, scheduler: AsyncIOScheduler):
    scheduler.remove_all_jobs()
    await call.message.answer(text="Рассылка остановлена", reply_markup=keymain.reset_keyboard())


@menu_router.callback_query(F.data == "update_data")
async def update_data_about_chats(call: types.CallbackQuery, session: AsyncSession, bot: Bot):
    bots = await session.execute(select(Session))
    chats = await session.execute(select(AllChats))
    chats = [b.chat_id for b in chats.scalars()]
    id_s = [b.user_id for b in bots.scalars()]
    for chat in chats:
        try:
            for i in id_s:
                user_channel_status = await bot.get_chat_member(chat_id=int(chat), user_id=int(i))
                print(user_channel_status)
                if user_channel_status.status != 'left':
                    await session.merge(Chat(chat_id=chat, bot_id=i))
                    await session.commit()
        except TelegramForbiddenError:
            continue
    await call.message.answer(text="Данные о ботах в чатах обновлены")

