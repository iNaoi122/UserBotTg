import pathlib
from pathlib import Path
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from fsm.state import AddPost
from database.model import Post

from kb.keymain import reset_keyboard

post_router = Router()


@post_router.callback_query(F.data == "createpost")
async def start_add_post(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(text="Добавьте медиа для поста", reply_markup=reset_keyboard())
    await state.set_state(AddPost.add_media)


@post_router.message(AddPost.add_media, F.photo)
async def add_media(message: types.Message, state: FSMContext):
    await state.update_data(
        media=None if message.text else
        (message.photo[-1].file_id if message.photo else
         (message.animation.file_id if message.animation else message.video.file_id)))
    file = await message.bot.download(file=message.photo[-1].file_id)
    with open(Path(Path.cwd(), "photos", f"{message.photo[-1].file_id}.png"), 'wb') as f:
        f.write(file.read())
    await state.update_data(path_media=f"{message.photo[-1].file_id}.png")
    await message.answer(text="Введите текст поста", reply_markup=reset_keyboard())
    await state.set_state(AddPost.add_text)


@post_router.message(AddPost.add_text, F.text)
async def add_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(text="Введите имя поста", reply_markup=reset_keyboard())
    await state.set_state(AddPost.add_name)


@post_router.message(AddPost.add_name, F.text)
async def add_name(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await session.merge(Post(media=data['media'], text=data['text'], name=data['name'], owner=message.from_user.id,
                             media_path=data["path_media"]))
    await session.commit()
    await message.answer(text="Вы успешно добавили пост", reply_markup=reset_keyboard())
    await state.clear()
