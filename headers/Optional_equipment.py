from aiogram import Router
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext

from backend.Keyboards import make_row_keyboard, make_column_keyboard
from loguru import logger


router = Router()


class StateClsOptionalEquipment(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    confirmation = State()  # подтверждение запроса
    end_of_script = State()  # завершение сценария


type_ts = ["Новый", "С пробегом(Б/У)"]


@router.message(Command(commands=["addOE"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Укажите состояние ТС на момент заключения договора",
                         reply_markup=make_column_keyboard(type_ts))
    await state.set_state(StateClsOptionalEquipment.processing_state)


@router.message(StateClsOptionalEquipment.processing_state, F.text.in_(type_ts[1]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await state.update_data(state_ts=message.text)
    await message.answer(text="Укажите вид оборудования")
    await state.set_state(StateClsOptionalEquipment.confirmation)


@router.message(StateClsOptionalEquipment.processing_state, F.text.in_(type_ts[0]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await state.update_data(state_ts=message.text)
    await message.answer(text=f'Для согласования установки дополнительного оборудования Вам необходимо:'
                              f'\n⦿ Запросить письмо у поставщика, подтверждающее сохранение гарантийных '
                              f'и/или иных обязательств, после установки вышеупомянутого оборудования'
                              f'\n⦿ Загрузить письмо от поставщика, подтверждающее сохранение гарантийных'
                              f'и/или иных обязательств, после установки вышеупомянутого оборудования.')
    await message.answer(text=f'Готовы загрузить письмо от поставщика в настоящее время?',
                         reply_markup=make_row_keyboard(["Да", "Нет"]))
    await state.set_state(StateClsOptionalEquipment.processing_data)


@router.message(StateClsOptionalEquipment.processing_data, F.text.casefold() == "да")
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Приложите письмо от поставщика в виде файла")
    await state.set_state(StateClsOptionalEquipment.prepare_data)


@router.message(StateClsOptionalEquipment.processing_data, F.text.casefold() == "нет")
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="После получения письма от поставщика снова выберите данный тип обращения в Telegram-боте")


@router.message(StateClsOptionalEquipment.prepare_data)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Обработка документов пользователя"""

    if document := message.document:
        logger.info(f'User : {message.from_user.id}  document_id: {document.file_id}')
        await state.update_data(document=document.file_id)

        # file = await bot.get_file(document.file_id)
        # file_path = file.file_path
        # await bot.download_file(file_path=file_path, destination=f"download_doc/{document.file_name}")

        await message.answer(text="Укажите вид оборудования")
        await state.set_state(StateClsOptionalEquipment.confirmation)
    else:
        await message.answer(text="Неверный формат сообщения")


@router.message(StateClsOptionalEquipment.confirmation)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Подтверждение заявки"""

    await state.update_data(type_equipment=message.text)

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    data = await state.get_data()
    await message.answer(text=f'Состояние тс - {data["state_ts"]}'
                         f'\nВид оборудования - {data["type_equipment"]}')

    await message.answer(text="Подтвердите создание обращения по установке дополнительного оборудования",
                         reply_markup=make_row_keyboard(["Подтвердить", "Отмена"]))
    await state.set_state(StateClsOptionalEquipment.end_of_script)


@router.message(StateClsOptionalEquipment.end_of_script, F.text.casefold() == "подтвердить")
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Формирование заявки"""

    await message.answer(text="Благодарим за обращение! Заявка на установку дополнительного оборудования принята.")
    await state.clear()


@router.message(StateClsOptionalEquipment.end_of_script, F.text.casefold() == "отмена")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="Благодарим за обращение! Действия отменены.")
    await state.clear()


