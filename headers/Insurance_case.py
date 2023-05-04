from contextlib import suppress
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, FSInputFile
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types

from backend.Keyboards import make_inline_keyboard, NumbersCallFactory, make_inline_keyboard_double, \
    make_inline_keyboard_one, replace_keyboard
from loguru import logger


router = Router()


class StateClsInsuranceCase(StatesGroup):
    processing_state = State()
    kasko_state = State()
    osago_state = State()

    kasko_difficulties = State()
    kasko_refusal = State()
    kasko_hijacking = State()

    letter_pay = State()
    letter_repair = State()
    franchise = State()


type_insurance = {
    "КАСКО" : "KASKO",
    "ОСАГО" : "OSAGO"
}

osago_methods = {
    "Действия при ДТП" : "osago_dtp",
    "Письмо на выплату" : "osago_payment_letter",
    "Сложности со страховой компанией" : "difficulties"
}

osago_letters = {
    "Распорядительное письмо на выплату" : "payment_letter",
    "Письмо о выдачи направления на ремонт" : "letter_repair",
    "Возмещение франшизы" : "franchise_reimb",
    "Возмещение УТС" : "payment_letterYTS"
}

kasko_methods = {
    "Действия при ДТП" : "dtp",
    "Письмо на выплату" : "payment_letter",
    "Сложности со страховой компанией" : "difficulties",
    "Отказ в урегулировании убытка" : "refusal",
    "Конструктивная гибель/угон" : "hijacking",
}

questions = [
    "Когда было подано заявление в страховую компанию? (дата)",
    "Введите дату страхового события",
    "Введите номер дела в страховой компании",
    "Вами подан полный комплект документов за исключением распорядительного письма?",
    "Транспортное средство предоставлено на осмотр в страховую компанию в поврежденном виде?",
    "Какие повреждения получил автомобиль? (в свободной форме)",
    "Ремонт транспортного средства уже осуществлен?",
    "Предоставлен ли ТС на осмотр в страховую компанию после ремонта?",
    "Опишите возникшие сложности",
    "В связи с чем вынесен отказ? Опишите ситуацию",
    "Задайте свой вопрос"
]

module = "Insurance_case"


@router.message(Command(commands=["insCase"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="По какому страховому случаю Вы обращаетесь?",
                         reply_markup=make_inline_keyboard(par=type_insurance,
                                                           module=module))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await state.set_state(StateClsInsuranceCase.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "KASKO"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ КАСКО """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=type_insurance,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(type_insurance=btn_pressed)
    await callback.message.answer(text="Выберите действие",
                                  reply_markup=make_inline_keyboard(par=kasko_methods,
                                                                    module=module))
    await state.set_state(StateClsInsuranceCase.kasko_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "dtp"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Действия при ДТП"""

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=kasko_methods,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(kasko_method=btn_pressed)
    await callback.message.answer(text="Здесь должна быть какая-то инструкция")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "hijacking"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ Конструктивная гибель/угон """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=kasko_methods,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(kasko_method=btn_pressed)
    await callback.message.answer(text="Задайте свой вопрос")
    await state.set_state(StateClsInsuranceCase.kasko_hijacking)


@router.message(StateClsInsuranceCase.kasko_hijacking)
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="Благодарим за обращение!")
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    data = await state.get_data()
    data.get("type_insurance") # тип страховки
    text = message.text        # текст обращения

    # Формирование обращения  Конструктивная гибель/угон

    await state.clear()


# Письмо на выплату НАЧАЛО
@router.callback_query(NumbersCallFactory.filter(F.action[:14] == "payment_letter"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Письмо на выплату для КАСКО и ОСАГО + Возмещение УТС"""

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    data = await state.get_data()

    with suppress(TelegramBadRequest):
        if data.get("type_insurance") == "KASKO":
            await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                                   keyboard=kasko_methods,
                                                                                   key_pressed=btn_pressed,
                                                                                   action="pressed"))
        else:
            await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                                   keyboard=osago_letters,
                                                                                   key_pressed=btn_pressed,
                                                                                   action="pressed"))

    await state.update_data(method_letter=btn_pressed)
    await state.set_state(StateClsInsuranceCase.letter_pay)

    if data.get("type_insurance") == "KASKO":
        await callback.message.answer(text=questions[0])
        await state.update_data(stage=1)
    else:
        await callback.message.answer(text="Введите номер полиса ОСАГО")
        await state.update_data(stage=0)


@router.message(StateClsInsuranceCase.letter_pay)
@logger.catch
async def stage(message: Message, state: FSMContext):
    data = await state.get_data()
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    if data['stage'] == 0:
        await state.update_data(number_osago=message.text)
        await message.answer(text=questions[0])
        await state.update_data(stage=1)
    if data['stage'] == 1:
        await state.update_data(date_statement=message.text)
        await message.answer(text=questions[1])
        await state.update_data(stage=2)
    elif data['stage'] == 2:
        await state.update_data(date_insured_event=message.text)
        await message.answer(text=questions[2])
        await state.update_data(stage=3)
    elif data['stage'] == 3:
        await state.update_data(number_deal=message.text)
        await message.answer(text=questions[3],
                             reply_markup=make_inline_keyboard_double(par={"Да": "stage_4_y", "Нет": "stage_4_n"},
                                                                      module=module,
                                                                      action="yn"))
        await state.update_data(stage=4)
    elif data['stage'] == 6:
        await state.update_data(damage_discription=message.text)
        await message.answer(text=questions[6],
                             reply_markup=make_inline_keyboard_double(par={"Да": "stage_7_y", "Нет": "stage_7_n"},
                                                                      module=module,
                                                                      action="yn"))
        await state.update_data(stage=7)


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_4'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    if btn_pressed == "y":
        await state.update_data(set_of_documents="Да")
    else:
        await state.update_data(set_of_documents="Нет")
    await state.update_data(stage=5)
    await callback.message.answer(text=questions[4],
                                  reply_markup=make_inline_keyboard_double(par={"Да": "stage_5_y", "Нет": "stage_5_n"},
                                                                           module=module,
                                                                           action="yn"))


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_5'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    if btn_pressed == "y":
        await state.update_data(damage_ts="Да")
    else:
        await state.update_data(damage_ts="Нет")
    await state.update_data(stage=6)
    await callback.message.answer(text=questions[5])


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_7'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    if btn_pressed == "y":
        await state.update_data(repair_ts="Да")
        await callback.message.answer(text=questions[7],
                                      reply_markup=make_inline_keyboard_double(par={"Да": "stage_8_y", "Нет": "stage_8_n"},
                                                                               module=module,
                                                                               action="yn"))
    else:
        await state.update_data(repair_ts="Нет")
        await callback.message.answer(text="Подтвердите создание обращения",
                                      reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn_lp", "Отмена": "cnl"},
                                                                               module=module,
                                                                               action="complete"))


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_8'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]

    if btn_pressed == "y":
        await state.update_data(insurance_inspection="Да")
    else:
        await state.update_data(insurance_inspection="Нет")
    await callback.message.answer(text="Подтвердите создание обращения",
                                  reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn_lp", "Отмена": "cnl_lp"},
                                                                           module=module,
                                                                           action="complete"))


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cnl'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Действия отменены.")
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cfn_lp'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Благодарим за обращение!")
    data = await state.get_data()
    answers = dict()

    # дата для письмо на выплату КАСКО
    if data.get("type_insurance") == "KASKO":
        answers = {
            "Тип страховки" : data.get("type_insurance"),
            "Действие" : data.get("method_letter"),
            questions[0] : data.get("date_statement"),
            questions[1] : data.get("date_insured_event"),
            questions[2] : data.get("number_deal"),
            questions[3] : data.get("set_of_documents"),
            questions[4] : data.get("damage_ts"),
            questions[5] : data.get("damage_discription"),
            questions[6] : data.get("repair_ts"),
            questions[7] : data.get("insurance_inspection") # может прилететь None
        }

    # дата для Распорядительное письмо на выплату ОСАГО
    if data.get("type_insurance") == "OSAGO" :
        answers = {
            "Тип страховки": data.get("type_insurance"),
            "Действие": data.get("method_letter"),
            "Номер полиса ОСАГО" : data.get("number_osago"),
            questions[0]: data.get("date_statement"),
            questions[1]: data.get("date_insured_event"),
            questions[2]: data.get("number_deal"),
            questions[3]: data.get("set_of_documents"),
            questions[4]: data.get("damage_ts"),
            questions[5]: data.get("damage_discription"),
            questions[6]: data.get("repair_ts"),
            questions[7]: data.get("insurance_inspection") # может прилететь None
        }

    # дата для Возмещение франшизы
    if data.get("method_letter") == "franchise_reimb":
        answers = {
            "Тип страховки": data.get("type_insurance"),
            "Действие": data.get("method_letter"),
            "Укажите дату страхового события" : data.get("date_event"),
            "Номер дела в страховой компании" : data.get("number_deal"),
            "Ремонт транспортного средства по КАСКО уже осуществлен?" : data.get("repair_ts"),
            "Предоставлен ли ТС на осмотр в страховую компанию после ремонта?" : data.get("insurance_inspection")  # может прилететь None
        }

    # Формирование обращения сюда ( 3 типа )

    await state.clear()
# Письмо на выплату КОНЕЦ


@router.callback_query(NumbersCallFactory.filter(F.action == "difficulties"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Сложности со страховой компанией для КАСКО и ОСАГО"""

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    data = await state.get_data()

    with suppress(TelegramBadRequest):
        if data.get("type_insurance") == "KASKO":
            await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                                   keyboard=kasko_methods,
                                                                                   key_pressed=btn_pressed,
                                                                                   action="pressed"))
        else:
            await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                                   keyboard=osago_methods,
                                                                                   key_pressed=btn_pressed,
                                                                                   action="pressed"))
    await state.update_data(kasko_method=btn_pressed)
    await callback.message.answer(text="Опишите возникшие сложности")
    await state.set_state(StateClsInsuranceCase.kasko_difficulties)


@router.message(StateClsInsuranceCase.kasko_difficulties)
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="Благодарим за обращение!")
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    data = await state.get_data()
    data.get("type_insurance") # тип страховки
    text = message.text        # текст обращения

    # Формирование обращения

    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "refusal"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ Отказ в урегулировании убытка """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=kasko_methods,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(kasko_method=btn_pressed)
    await callback.message.answer(text="В связи с чем вынесен отказ? Опишите ситуацию")
    await state.set_state(StateClsInsuranceCase.kasko_refusal)


@router.message(StateClsInsuranceCase.kasko_refusal)
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="Благодарим за обращение!")
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    text = message.text  # тут текст обращения от пользователя

    # Формирование обращения    Отказ в урегулировании убытка

    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "OSAGO"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ ОСАГО """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=type_insurance,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(type_insurance=btn_pressed)
    await callback.message.answer(text="Выберите действие",
                                  reply_markup=make_inline_keyboard(par=osago_methods,
                                                                    module=module))
    await state.set_state(StateClsInsuranceCase.osago_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "osago_dtp"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Действия при ДТП ОСАГО"""

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=osago_methods,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(osago_method=btn_pressed)

    await callback.message.answer(text="Здесь должна быть какая-то инструкция") # уточнить

    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "osago_payment_letter"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ Письмо на выплату ОСАГО"""

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=osago_methods,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(osago_method=btn_pressed)
    await callback.message.answer(text="Выберите действие",
                                  reply_markup=make_inline_keyboard(par=osago_letters,
                                                                    module=module))


@router.callback_query(NumbersCallFactory.filter(F.action == "letter_repair"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ Письмо о выдачи направления на ремонт """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=osago_letters,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(method_letter=btn_pressed)
    await state.set_state(StateClsInsuranceCase.letter_repair)

    await callback.message.answer(text="Введите номер полиса ОСАГО")
    await state.update_data(stage=0)


@router.message(StateClsInsuranceCase.letter_repair)
@logger.catch
async def stage(message: Message, state: FSMContext):
    data = await state.get_data()
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    if data['stage'] == 0:
        await state.update_data(number_osago=message.text)
        await message.answer(text=questions[0])
        await state.update_data(stage=1)
    if data['stage'] == 1:
        await state.update_data(date_statement=message.text)
        await message.answer(text=questions[1])
        await state.update_data(stage=2)
    elif data['stage'] == 2:
        await state.update_data(date_insured_event=message.text)
        await message.answer(text=questions[2])
        await state.update_data(stage=3)
    elif data['stage'] == 3:
        await state.update_data(number_deal=message.text)
        await message.answer(text=questions[4],
                             reply_markup=make_inline_keyboard_double(par={"Да": "stage_1_y", "Нет": "stage_1_n"},
                                                                      module=module,
                                                                      action="yn"))
        await state.update_data(stage=4)


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_1'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    if btn_pressed == "y":
        await state.update_data(damage_ts="Да")
    else:
        await state.update_data(damage_ts="Нет")

    await state.update_data(stage=5)
    await callback.message.answer(text=questions[6],
                                  reply_markup=make_inline_keyboard_double(par={"Да": "stage_2_y", "Нет": "stage_2_n"},
                                                                           module=module,
                                                                           action="yn"))


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_2'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    if btn_pressed == "y":
        await state.update_data(repair_ts="Да")
    else:
        await state.update_data(repair_ts="Нет")

    await callback.message.answer(text="Подтвердите создание обращения",
                                  reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn_lp", "Отмена": "cnl_lp"},
                                                                           module=module,
                                                                           action="complete"))


@router.callback_query(NumbersCallFactory.filter(F.action == "franchise_reimb"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """ Возмещение франшизы """

    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=osago_letters,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(method_letter=btn_pressed)
    await state.set_state(StateClsInsuranceCase.letter_repair)

    await callback.message.answer(text="Укажите дату страхового события")
    await state.set_state(StateClsInsuranceCase.franchise)
    await state.update_data(stage=0)


@router.message(StateClsInsuranceCase.franchise)
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    data = await state.get_data()

    if data.get("stage") == 0:
        await state.update_data(date_event=message.text)
        await message.answer(text="Введите номер дела в страховой компании")
        await state.update_data(stage=1)
    elif data.get("stage") == 1:
        await state.update_data(number_deal=message.text)
        await message.answer(text="Ремонт транспортного средства по КАСКО уже осуществлен?",
                             reply_markup=make_inline_keyboard_double(par={"Да": "stage_k_y", "Нет": "stage_k_n"},
                                                                      module=module,
                                                                      action="yn"))


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_k'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    if btn_pressed == "y":
        await state.update_data(repair_ts="Да")
        await callback.message.answer(text="Предоставлен ли ТС на осмотр в страховую компанию после ремонта?",
                                      reply_markup=make_inline_keyboard_double(par={"Да": "stage_g_y", "Нет": "stage_g_n"},
                                                                               module=module,
                                                                               action="yn"))
    else:
        await state.update_data(repair_ts="Нет")
        await callback.message.answer(text="Подтвердите создание обращения",
                                      reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn_lp", "Отмена": "cnl_lp"},
                                                                               module=module,
                                                                               action="complete"))


@router.callback_query(NumbersCallFactory.filter(F.value[:22] == f'{module}_stage_g'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    btn_pressed = callback.data.split(":")[2][23:24]

    if btn_pressed == "y":
        await state.update_data(insurance_inspection="Да")
    else:
        await state.update_data(insurance_inspection="Нет")

    await callback.message.answer(text="Подтвердите создание обращения",
                                  reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn_lp", "Отмена": "cnl_lp"},
                                                                           module=module,
                                                                           action="complete"))