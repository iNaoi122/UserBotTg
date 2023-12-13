from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database.model import Session

from kb.selectbot import select_bot_key, update_key
from kb.keymain import reset_keyboard

bot_router = Router()


@bot_router.callback_query(F.data == "editbot")
async def edit_bot(call: types.CallbackQuery, session: AsyncSession):
    bots = await session.execute(
        select(Session).where(Session.owner == int(call.message.chat.id)).order_by(Session.id).limit(4))
    bots = [d.name for d in bots.scalars()]
    await call.message.answer(text="Выберите аккаунт", reply_markup=select_bot_key(bots))


@bot_router.callback_query(F.data.startswith("edit:selectbot_back"))
@bot_router.callback_query(F.data.startswith("edit:selectbot_back"))
async def pagination(call: types.CallbackQuery, session: AsyncSession):
    data = await session.execute(
        select(Session).where(Session.owner == int(call.message.chat.id)).order_by(Session.id).limit(4).offset(
            int(call.data.split(":")[1])))
    names = [d.name for d in data.scalars()]
    await call.message.edit_reply_markup(reply_markup=select_bot_key(names, int(call.data.split(":")[1])))


@bot_router.callback_query(F.data.startswith("edit:selectbot"))
async def select_post(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    bot_data = await session.execute(select(Session).where(Session.owner == int(call.message.chat.id))
                                     .where(Session.name == call.data.split(':')[2]))
    bot_data = bot_data.scalars().first()
    await call.message.answer(text="Вы выбрали аккаунт " + bot_data.name, reply_markup=update_key())
    await state.update_data(id=bot_data.id)


@bot_router.callback_query(F.data == "bot_update:delete")
async def delete_bot(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    await session.execute(delete(Session).where(Session.owner == int(call.message.chat.id)).where(Session.id == int(data['id'])))
    await session.commit()
    await call.message.answer(text="Бот удален", reply_markup=reset_keyboard())
    await state.clear()