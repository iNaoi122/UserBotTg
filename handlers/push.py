import random

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client

from fsm.state import Push
from database.model import Post, Session, Chat
from kb.pushpost import select_post_key, select_bot_key
from kb.keymain import reset_keyboard

from sendler.send_message import Clients

push_router = Router()


@push_router.callback_query(F.data == "createpush")
async def select_post(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await session.execute(select(Post).order_by(Post.id).limit(4))
    names = [d.name for d in data.scalars()]
    await call.message.answer(text="Выберите пост для рассылки", reply_markup=select_post_key(names))


@push_router.callback_query(F.data.startswith("createpush_back"))
@push_router.callback_query(F.data.startswith("createpush_next"))
async def pagination(call: types.CallbackQuery, session: AsyncSession):
    data = await session.execute(
        select(Post).where(Post.owner == int(call.message.chat.id)).order_by(Post.id).limit(4).offset(
            int(call.data.split(":")[1])))
    names = [d.name for d in data.scalars()]
    await call.message.edit_reply_markup(reply_markup=select_post_key(names, int(call.data.split(":")[1])))


@push_router.callback_query(F.data.startswith("pushpost"))
async def get_post(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    post_data = await session.execute(select(Post).where(Post.owner == int(call.message.chat.id)).where(
        Post.name == f"{call.data.split(':')[1]}"))
    post_data = post_data.scalars().first()
    await state.update_data(post=post_data)
    bot_data = await session.execute(select(Session).order_by(Session.id).limit(4))
    names = [d.name for d in bot_data.scalars()]
    await call.message.edit_text(text="Выберите аккаунт для отправки",
                                 reply_markup=select_bot_key(names))


@push_router.callback_query(F.data.startswith("selectbot_back"))
@push_router.callback_query(F.data.startswith("selectbot_next"))
async def pagination(call: types.CallbackQuery, session: AsyncSession):
    data = await session.execute(
        select(Session).where(Session.owner == int(call.message.chat.id)).order_by(Session.id).limit(4).offset(
            int(call.data.split(":")[1])))
    names = [d.name for d in data.scalars()]
    await call.message.edit_reply_markup(reply_markup=select_post_key(names, int(call.data.split(":")[1])))


@push_router.callback_query(F.data.startswith("selectbot"))
async def select_bot(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    bot_data = await session.execute(select(Session).where(Session.name == f"{call.data.split(':')[1]}"))
    bot_data = bot_data.scalars().first()
    await state.update_data(bot=bot_data)
    await call.message.answer(text="Введите период отправки сообщений")
    await state.set_state(Push.input_time)


@push_router.message(Push.input_time)
async def input_time(message: types.Message, state: FSMContext, scheduler: AsyncIOScheduler, session: AsyncSession,
                     process: Clients):
    if not message.text.strip().isdigit():
        await message.answer(text="Введите число")
    else:

        data = await state.get_data()
        async with Client(name=data["bot"].name, session_string=data['bot'].session_string) as client:
            client: Client
            bot_id = await client.get_me()
            if client.is_connected:
                chats = await session.execute(select(Chat).where(Chat.bot_id == f"{bot_id.id}"))
                await process.do_add_new_client(name=data["bot"].name, session_string=data['bot'].session_string)
                for chat in chats.scalars():
                    chat: Chat
                    scheduler.add_job(process.do_send_message, trigger="interval",
                                      max_instances=10,
                                      seconds=int(message.text.strip()) + random.randint(-2, 2),
                                      args=[
                                          {"account": data["bot"].name, "chat": chat.chat_id, "text": data['post'].text,
                                           "photo": data['post'].media_path, "owner":int(message.from_user.id)}])

                await message.answer(text="Рассылка успешно начата", reply_markup=reset_keyboard())
            else:
                await message.answer(text=f"Этот аккаунт {data['bot'].name}  аккаунт заблокирован")
