from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from kb.selectpost import select_post_key, update_key

from fsm.state import EditPost
from database.model import Post
from kb.keymain import reset_keyboard

edit_router = Router()


@edit_router.callback_query(F.data == "editpost")
async def edit_post(call: types.CallbackQuery, session: AsyncSession):
    print(call.message.chat.id)
    data = await session.execute(select(Post).where(Post.owner == int(call.message.chat.id)).order_by(Post.id).limit(4))
    names = [d.name for d in data.scalars()]
    await call.message.answer(text="Выберите пост", reply_markup=select_post_key(names))


@edit_router.callback_query(F.data.startswith("selectpost_back"))
@edit_router.callback_query(F.data.startswith("selectpost_next"))
async def pagination(call: types.CallbackQuery, session: AsyncSession):
    data = await session.execute(select(Post).where(Post.owner == int(call.message.chat.id)).order_by(Post.id).limit(4).offset(int(call.data.split(":")[1])))
    names = [d.name for d in data.scalars()]
    await call.message.edit_reply_markup(reply_markup=select_post_key(names, int(call.data.split(":")[1])))


@edit_router.callback_query(F.data.startswith("selectpost"))
async def select_post(call: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    post_data = await session.execute(select(Post).where(Post.owner == int(call.message.chat.id)).where(Post.name == f"{call.data.split(':')[1]}"))
    post_data = post_data.scalars().first()
    await call.message.answer_photo(caption=post_data.text, photo=post_data.media, reply_markup=update_key())
    await state.update_data(id=post_data.id)


@edit_router.callback_query(F.data.startswith("update"))
async def select_data(call: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if call.data.split(":")[1] == "photo":
        await call.message.answer(text="Добавьте новое фото", reply_markup=reset_keyboard())
        await state.set_state(EditPost.UpdateData)
    elif call.data.split(":")[1] == "text":
        await call.message.answer(text="Добавьте новый текст", reply_markup=reset_keyboard())
        await state.set_state(EditPost.UpdateData)
    elif call.data.split(":")[1] == "delete":
        await session.execute(delete(Post).where(Post.id == data['id']))
        await session.commit()
        await call.message.answer(text="Пост удален", reply_markup=reset_keyboard())


@edit_router.message(EditPost.UpdateData, F.photo)
async def update_data_photo(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await session.execute(update(Post).where(Post.id == data['id']).values(media=message.photo[-1].file_id))
    await session.commit()
    new_post = await session.execute(select(Post).where(Post.id == data['id']))
    new_post = new_post.scalars().first()
    post_id = data['id']
    await state.clear()
    await state.update_data(id=post_id)
    await message.answer_photo(caption=new_post.text, photo=new_post.media, reply_markup=update_key())


@edit_router.message(EditPost.UpdateData, F.text)
async def update_data_text(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await session.execute(update(Post).where(Post.id == data['id']).values(text=message.text))
    await session.commit()
    new_post = await session.execute(select(Post).where(Post.id == data['id']))
    new_post = new_post.scalars().first()
    post_id = data['id']
    await state.clear()
    await state.update_data(id=post_id)
    await message.answer_photo(caption=new_post.text, photo=new_post.media, reply_markup=update_key())
