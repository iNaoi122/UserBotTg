from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_post_key(data: list, offset: int = 0):
    keyboard = [
        [InlineKeyboardButton(text=f"{d}", callback_data=f"selectpost:{d}") for d in data],
        [InlineKeyboardButton(text="<-", callback_data=f"selectpost_back:{offset - 4}"),
         InlineKeyboardButton(text="->", callback_data=f"selectpost_next:{offset + 4}")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def update_key():
    keyboard = [
        [InlineKeyboardButton(text="Изменить фото", callback_data="update:photo")],
        [InlineKeyboardButton(text="Изменить текст", callback_data="update:text")],
        [InlineKeyboardButton(text="Удалить пост", callback_data="update:delete")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)