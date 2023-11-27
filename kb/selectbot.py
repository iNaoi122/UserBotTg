from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_bot_key(data: list, offset: int = 0):
    keyboard = [
        [InlineKeyboardButton(text=f"{d}", callback_data=f"edit:selectbot:{d}") for d in data],
        [InlineKeyboardButton(text="<-", callback_data=f"edit:selectbot_back:{offset - 4}"),
         InlineKeyboardButton(text="->", callback_data=f"edit:selectbot_next:{offset + 4}")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def update_key():
    keyboard = [
        [InlineKeyboardButton(text="Удалить бота", callback_data="bot_update:delete")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)