from aiogram import Router
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile

from Keyboards import make_row_keyboard, make_column_keyboard, make_inline_keyboard
from loguru import logger


router = Router()


class StateClsChangeCEO(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


change_variable = [
    "Генеральный директор",
    "Директор",
    "ЕИО",
    "Бенефициар"
]


@router.message(Command(commands=["changeCEO"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Кто именно сменился в Вашей компании?",
                         reply_markup=make_column_keyboard(change_variable))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsChangeCEO.processing_state)


@router.message(StateClsChangeCEO.processing_state, F.text.in_(change_variable))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Информируем пользователя о перечне документов"""

    await state.update_data(change_var=message.text)
    if message.text == "Бенефициар":
        await message.answer(
            text=f'Для формирования запроса на изменение руководителя организации Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Копия паспорта нового руководителя (разворот с фотографией, пропиской, и сведения о ранее выданных паспортах) - заверенная копия'
                 f'\n⦿ Протокол/решение о назначении - заверенная копия'
                 f'\n⦿ Приказ о назначении Генерального директора - заверенная копия'
                 f'\n⦿ Согласие на обработку персональных данных руководителя'
                 f'\n⦿ Анкета'
                 f'\n⦿ Комфортное письмо'
                 f'\nДокументы необходимо прикрепить файлами в данный Telegram бот.')
    else:
        await message.answer(
            text=f'Для формирования запроса на изменение руководителя организации Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Копия паспорта нового руководителя (разворот с фотографией, пропиской, и сведения о ранее выданных паспортах) - заверенная копия'
                 f'\n⦿ Протокол/решение о назначении - заверенная копия'
                 f'\n⦿ Приказ о назначении Генерального директора - заверенная копия'
                 f'\n⦿ Согласие на обработку персональных данных руководителя'
                 f'\n⦿ Анкета'
                 f'\nДокументы необходимо прикрепить файлами в данный Telegram бот.')


    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    sopd = FSInputFile('files/СОПД.pdf')
    # anketa = FSInputFile('files/')   #уточнить

    await message.answer_document(sopd)
    await message.answer(text='Готовы ли Вы сейчас приложить указанные документы?',
                         reply_markup=make_row_keyboard(["Да", "Нет"]))
    await state.set_state(StateClsChangeCEO.processing_data)


@router.message(StateClsChangeCEO.processing_data, F.text.casefold() == "нет")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text='Когда будете готовы приложить все вышеуказанные документы снова выберите данный тип обращения в Telegram - боте')
    await state.clear()


@router.message(StateClsChangeCEO.processing_data, F.text.casefold() == "да")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="После того, как приложите все документы, введите \"Завершить\"")

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsChangeCEO.prepare_data)


@router.message(StateClsChangeCEO.prepare_data, F.text.casefold() == "завершить")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="Подтвердите создание обращения по уточнению назначения платежа",
                         reply_markup=make_row_keyboard(["Подтвердить", "Отмена"]))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsChangeCEO.end_of_script)


@router.message(StateClsChangeCEO.prepare_data)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Обработка документов пользователя"""

    if document := message.document:
        logger.info(f'User : {message.from_user.id}  document_id: {document.file_id}')
        # await redis.append(key=str(message.from_user.id), value=str(document.file_id))
        # file = await bot.get_file(document.file_id)
        # file_path = file.file_path
        # await bot.download_file(file_path=file_path, destination=f"download_doc/{document.file_name}")
    else:
        await message.answer(text='Неверный формат сообщения')


@router.message(StateClsChangeCEO.end_of_script, F.text.casefold() == "отмена")
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Благодарим за обращение! Действия отменены.")
    await state.clear()


@router.message(StateClsChangeCEO.end_of_script)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Завершение обработки документов, формирование заявки"""

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await message.answer(text='Благодарим за обращение!')

    # data = await state.get_data()
    # text = f'\nUser : {message.from_user.id} \nType_: {data["name_reorg"]} \nmethod_feedback : {data["method_feedback"]}'
    # logger.success(text)

    await state.clear()


