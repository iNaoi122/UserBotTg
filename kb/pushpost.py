from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def select_post_key(data: list, offset: int = 0):
    keyboard = [
        [InlineKeyboardButton(text=f"{d}", callback_data=f"pushpost:{d}") for d in data],
        [InlineKeyboardButton(text="<-", callback_data=f"pushpost_back:{offset - 4}"),
         InlineKeyboardButton(text="->", callback_data=f"pushpost_next:{offset + 4}")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def select_bot_key(data: list, offset: int = 0):
    keyboard = [
        [InlineKeyboardButton(text=f"{d}", callback_data=f"selectbot:{d}") for d in data],
        [InlineKeyboardButton(text="<-", callback_data=f"selectbot_back:{offset - 4}"),
         InlineKeyboardButton(text="->", callback_data=f"selectbot_next:{offset + 4}")],
        [InlineKeyboardButton(text="Назад", callback_data="reset")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

