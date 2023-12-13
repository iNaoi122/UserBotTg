from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    key = [
        [InlineKeyboardButton(text="Создать пост", callback_data="createpost")],
        [InlineKeyboardButton(text="Редактировать посты", callback_data="editpost")],
        [InlineKeyboardButton(text="Добавить юзербота", callback_data="adduserbot")],
        [InlineKeyboardButton(text="Управление юзерботами", callback_data="editbot")],

        [InlineKeyboardButton(text="Создать рассылку", callback_data="createpush")],
        # [InlineKeyboardButton(text="Обновить данные о ботах в чатах", callback_data="update_data")],
        [InlineKeyboardButton(text="Остановить рассылку", callback_data="stop")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=key)


def reset_keyboard():
    key = [
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=key)
