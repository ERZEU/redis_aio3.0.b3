from contextlib import suppress
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram import types

from backend.Keyboards import make_inline_keyboard, NumbersCallFactory, make_inline_keyboard_double, \
    make_inline_keyboard_one, replace_keyboard
from loguru import logger


router = Router()
module = "Change_of_CEO"


class StateClsChangeCEO(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


change_variable = {
    "Генеральный директор" : "ceo",
    "Директор" : "dir",
    "ЕИО" : "eio",
    "Бенефициар" : "ben"
}


@router.message(Command(commands=["changeCEO"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Кто именно сменился в Вашей компании?",
                         reply_markup=make_inline_keyboard(par=change_variable, module=module))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsChangeCEO.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.module == f'{module}_CONF'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Информируем пользователя о перечне документов"""

    btn_pressed = callback.data.split(":")[3]

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=change_variable,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(change_var=btn_pressed)
    if callback.data == f'fabnum:{module}:confirm:ben':
        await callback.message.answer(
            text=f'Для формирования запроса на изменение руководителя организации Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Копия паспорта нового руководителя (разворот с фотографией, пропиской, и сведения о ранее выданных паспортах) - заверенная копия'
                 f'\n⦿ Протокол/решение о назначении - заверенная копия'
                 f'\n⦿ Приказ о назначении Генерального директора - заверенная копия'
                 f'\n⦿ Согласие на обработку персональных данных руководителя'
                 f'\n⦿ Анкета'
                 f'\n⦿ Комфортное письмо'
                 f'\nДокументы необходимо прикрепить файлами в данный Telegram бот.')
    else:
        await callback.message.answer(
            text=f'Для формирования запроса на изменение руководителя организации Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Копия паспорта нового руководителя (разворот с фотографией, пропиской, и сведения о ранее выданных паспортах) - заверенная копия'
                 f'\n⦿ Протокол/решение о назначении - заверенная копия'
                 f'\n⦿ Приказ о назначении Генерального директора - заверенная копия'
                 f'\n⦿ Согласие на обработку персональных данных руководителя'
                 f'\n⦿ Анкета'
                 f'\nДокументы необходимо прикрепить файлами в данный Telegram бот.')

    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')

    sopd = FSInputFile('./files/СОПД.pdf')
    # anketa = FSInputFile('files/')   #уточнить

    await callback.message.answer_document(sopd)
    await callback.message.answer(text='Готовы ли Вы сейчас приложить указанные документы?',
                                  reply_markup=make_inline_keyboard_double(par={"Да": "yes", "Нет": "no"},
                                                                           module=module,
                                                                           action="yn"))

    await state.set_state(StateClsChangeCEO.processing_data)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_no'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):

    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Когда будете готовы приложить все вышеуказанные документы снова выберите данный тип обращения в Telegram - боте')
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_yes'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="После того, как приложите все документы, нажмите кнопку ниже",
                                  reply_markup=make_inline_keyboard_one(module=module,
                                                                        text="Завершить",
                                                                        action="doc_conf"))

    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')

    await state.set_state(StateClsChangeCEO.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.action == f'{module}_doc_conf'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="Подтвердите создание обращения по уточнению назначения платежа",
                                  reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn", "Отмена": "cnl"},
                                                                           module=module,
                                                                           action="complete"))

    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')

    await state.set_state(StateClsChangeCEO.end_of_script)


@router.message(StateClsChangeCEO.prepare_data)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Обработка документов пользователя"""

    if document := message.document:
        logger.info(f'User : {message.from_user.id}  document_id: {document.file_id}')
        # сохранение документа в байт коде

    else:
        await message.answer(text='Неверный формат сообщения')


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cnl'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')
    await callback.message.answer(text="Действия отменены.")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cfn'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Завершение обработки документов, формирование заявки"""

    await callback.message.delete_reply_markup()
    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')

    await callback.message.answer(text='Благодарим за обращение!')

    # data = await state.get_data()
    # text = f'\nUser : {message.from_user.id} \nType_: {data["name_reorg"]} \nmethod_feedback : {data["method_feedback"]}'
    # logger.success(text)

    await state.clear()


