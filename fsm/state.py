from aiogram.fsm.state import State, StatesGroup


class AddPost(StatesGroup):
    add_media = State()
    add_text = State()
    add_name = State()


class EditPost(StatesGroup):
    UpdateData = State()


class AddBot(StatesGroup):
    add_api = State()
    add_name = State()
    send_code = State()
    get_code = State()


class Push(StatesGroup):
    input_time = State()