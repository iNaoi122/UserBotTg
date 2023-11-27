from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from pyrogram import Client
from pyrogram.errors.exceptions import FloodWait

import kb.keymain
from fsm.state import AddBot
from database.model import Session
from sendler.send_message import Clients

add_router = Router()


@add_router.callback_query(F.data == "adduserbot")
async def add_bot(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(text="Введите api_id|api_hash|phone в формате указанном выше"
                                   "Получить их можно тут https://my.telegram.org/apps",
                              reply_markup=kb.keymain.reset_keyboard())
    await state.set_state(AddBot.add_name)


@add_router.message(AddBot.add_name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(api=message.text)
    await message.answer(text="Введите имя пользователя (уникальное)")
    await state.set_state(AddBot.send_code)


@add_router.message(AddBot.send_code)
async def send_code(message: types.Message, state: FSMContext, session: AsyncSession, process: Clients):
    data = await state.get_data()
    await state.update_data(name=message.text.strip())
    client = Client(name=message.text.strip(), api_id=data['api'].split("|")[0], api_hash=data['api'].split("|")[1],
                    in_memory=True)
    try:
        await client.connect()
        await client.storage.user_id(1)
        string = await client.export_session_string()
        print(client.me.id)
        await client.send_message("me", "some")
        await client.stop()
        await session.merge(Session(name=message.text.strip(), session_string=string))
        await session.commit()
        await message.answer(text="Сессия создана", reply_markup=kb.keymain.reset_keyboard())
        await process.do_add_new_client(name=message.text.strip(), session_string=string)
        await state.clear()
    except FloodWait:
        await message.answer(text="Подождите некоторое время перед созданием новой сессии")

    except AttributeError:
        phone_code = await client.send_code(phone_number=data['api'].split("|")[2])
        await state.update_data(hash=phone_code.phone_code_hash)
        await state.update_data(client=client)
        await message.answer(text="Введите код из сообщения в тг, в коде поставьте пробел",
                             reply_markup=kb.keymain.reset_keyboard())
        await state.set_state(AddBot.get_code)


@add_router.message(AddBot.get_code)
async def get_code(message: types.Message, state: FSMContext, session: AsyncSession, process: Clients):
    data = await state.get_data()
    client: Client = data['client']
    try:
        await client.sign_in(phone_number=data['api'].split("|")[2], phone_code_hash=data['hash'],
                             phone_code=message.text.replace(" ", "").strip())
        await client.storage.user_id(1)
        string = await client.export_session_string()
        info = await client.get_me()
        await session.merge(Session(name=data['name'], session_string=string, user_id=info.id,
                                    owner=message.from_user.id))
        await session.commit()
        await message.answer(text="Регистрация прошла успешно", reply_markup=kb.keymain.reset_keyboard())
        await process.do_add_new_client(name=data['name'], session_string=string)
    except Exception as e:
        print(e)
        await message.answer(text="Ошибка при регистрации", reply_markup=kb.keymain.reset_keyboard())
    await state.clear()
