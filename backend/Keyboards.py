from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.dispatcher.filters.callback_data import CallbackData


class NumbersCallFactory(CallbackData, prefix="fabnum"):
    value: str
    action: str


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


def make_inline_keyboard(par: dict[str], action="static"):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in par.items():
        keyboard_builder.button(text="🔵 "+text_but, callback_data=NumbersCallFactory(value=val_but, action=action))

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


def replace_keyboard(keyboard, key_pressed, action):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in keyboard.items():
        if val_but == key_pressed:
            keyboard_builder.button(text="🔘 "+text_but, callback_data=NumbersCallFactory(value=val_but, action=action))
        else:
            keyboard_builder.button(text="🔵 "+text_but, callback_data=NumbersCallFactory(value=val_but, action=action))

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
