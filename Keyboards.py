from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """Создаёт реплай-клавиатуру с кнопками в один ряд"""
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True, one_time_keyboard=True)


def make_column_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """Создаёт реплай-клавиатуру с кнопками в несколько рядов"""
    builder = ReplyKeyboardBuilder()
    for i in items:
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)