from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardButton
from aiogram.dispatcher.filters.callback_data import CallbackData


class NumbersCallFactory(CallbackData, prefix="fabnum"):
    module: str
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


def make_inline_keyboard_one(module, text, action):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard_builder.button(text=text,
                            callback_data=NumbersCallFactory(module=module,
                                                             value="once_key",
                                                             action=f'{module}_{action}'))

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


def make_inline_keyboard_double(par: dict[str], module, action):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in par.items():
        keyboard_builder.button(text=text_but,
                                callback_data=NumbersCallFactory(module=module,
                                                                 value=f'{module}_{val_but}',
                                                                 action=action))

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()


def make_inline_keyboard(par: dict[str], module, action="switch"):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in par.items():
        keyboard_builder.button(text="🔵 "+text_but,
                                callback_data=NumbersCallFactory(module=module, value=val_but, action=action))

    keyboard_builder.button(text="Подтвердить", callback_data=NumbersCallFactory(module=module, value="confirm", action="err"))
    keyboard_builder.adjust(1)
    keyboard_builder.button(text="Отмена", callback_data=NumbersCallFactory(module=module, value="cancel", action="cancel"))

    return keyboard_builder.as_markup()


def replace_keyboard(module, keyboard, key_pressed, action="static"):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in keyboard.items():
        if val_but == key_pressed:
            keyboard_builder.button(text="🔘 "+text_but,
                                    callback_data=NumbersCallFactory(module=module, value=val_but, action=action))
        else:
            keyboard_builder.button(text="🔵 "+text_but,
                                    callback_data=NumbersCallFactory(module=module, value=val_but, action=action))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


