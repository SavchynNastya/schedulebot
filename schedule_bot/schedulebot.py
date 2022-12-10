from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TOKEN_API
from db import ScheduleDB
from kb import ikb_group, ikb_wd, ikb_days, ikb_changeweek, \
    ikb_chooseday, ikb_admin, ikb_group_add, ikb_chooseweek, \
    ikb_setday, ikb_choose_to_change, ikb_go_back_classnum, ikb_change_lectsub, ikb_group_modify, \
    ikb_week_modify, ikb_day_modify, ikb_which_change, ikb_group_delete, ikb_week_delete, ikb_day_delete, ikb_add_class, \
    ikb_setclass, ikb_modify_class, ikb_modify_from_add, ikb_add_from_modify
import logging
import datetime

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

db = ScheduleDB()

admins = [529541562]
moderators = []

HELP = """<b><em>/start</em></b> - розпочати роботу 
    <b><em>/help</em></b> - список команд
    <b><em>/setgroup</em></b> - обрати академічну групу
    <b><em>/current</em></b> - поточне заняття
    <b><em>/next</em></b> - наступне заняття
    <b><em>/time</em></b> - скільки часу до початку заняття чи до його кінця
    <b><em>/today</em></b> - розклад на сьогодні
    <b><em>/tomorrow</em></b> - розклад на завтра
    <b><em>/weekday</em></b> - розклад на певний тиждень чи конкретний день
    <b><em>/admin</em></b> - можливості адміна
    """


async def anti_spam(*args, **kwargs):
    message = args[0]
    await message.answer("Зачекайте трохи...")
    await message.delete


class Info(StatesGroup):
    group = State()
    # period = State()
    day = State()
    type_of_week = State()


class Coincidence(StatesGroup):
    id = State()
    group = State()
    day = State()
    type_of_week = State()
    class_num = State()
    classroom = State()

    lecturer = State()
    max_lecturers = State()
    subject = State()
    sub_lec = State()
    save_ids = State()


class AddClass(StatesGroup):
    group = State()
    day = State()
    type_of_week = State()
    class_num = State()
    classroom = State()
    sub_lec = State()
    setted_classes = State()


class ModifyClass(StatesGroup):
    group = State()
    day = State()
    type_of_week = State()
    class_num = State()
    classroom = State()
    sub_lec = State()
    available_classes = State()
    save_ids = State()
    max_lecturers = State()


class DeleteClass(StatesGroup):
    group = State()
    day = State()
    type_of_week = State()
    class_num = State()
    available_classes = State()


class SetAdmin(StatesGroup):
    id = State()


def get_week_type():
    # поточний час
    now = datetime.datetime.now()
    week = now.isocalendar()[1] - now.replace(day=1).isocalendar()[1] + 1

    # поточний тиждень - парний чи ні
    if not week % 2:
        week = "Парний"
    else:
        week = "Непарний"

    return week


@dp.message_handler(commands=['start'])
@dp.throttled(anti_spam, rate=1)
async def cmd_start(message: types.Message) -> None:
    await message.answer('Привіт!\n'
                         'Щоб дізнатись розклад академічної групи - обери її за командою /setgroup\n')
    await message.delete()


@dp.message_handler(commands=['setgroup'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_setgroup(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    await message.answer("Обери групу:", reply_markup=ikb_group)


@dp.message_handler(commands=['admin'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_admin(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id in admins or message.from_user.username in moderators:
        await message.answer(f"Вітаю, {message.from_user.first_name}", reply_markup=ikb_admin)
    else:
        await message.answer("Вибачте, ви не є адміністратором")
    await message.delete()


@dp.message_handler(commands=['help'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_help(message: types.Message):
    await message.answer(text=HELP, parse_mode="HTML")
    await message.delete()


@dp.message_handler(commands=['cancel'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    if state is None:
        return
    logging.info('Cancelling state %r', state)
    await state.finish()
    await message.answer("Дії було перервано")
    await message.delete()


@dp.message_handler(commands=['weekday'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_weekday(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    data = await state.get_data()
    if 'group' not in data:
        await message.answer("Вам спершу необхідно обрати групу - /setgroup")

    else:
        await message.answer("Оберіть опцію...", reply_markup=ikb_wd)
        await message.delete()


@dp.message_handler(commands=['current'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_current(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    data = await state.get_data()
    if 'group' not in data:
        await message.answer("Вам спершу необхідно обрати групу - /setgroup")

    else:
        await Info.type_of_week.set()
        state = dp.get_current().current_state()
        await state.update_data(type_of_week=get_week_type())

        await Info.day.set()
        state = dp.get_current().current_state()
        await state.update_data(day=datetime.datetime.now().weekday())

        data = await state.get_data()

        schedule = db.get_current(data['group'], data['type_of_week'], data['day'],
                                  datetime.datetime.now().hour, datetime.datetime.now().minute)

        await message.answer(f"{schedule}", parse_mode="HTML")
        await message.delete()


@dp.message_handler(commands=['next'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_next(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    data = await state.get_data()
    if 'group' not in data:
        await message.answer("Вам спершу необхідно обрати групу - /setgroup")

    else:
        await Info.type_of_week.set()
        state = dp.get_current().current_state()
        await state.update_data(type_of_week=get_week_type())

        await Info.day.set()
        state = dp.get_current().current_state()
        await state.update_data(day=datetime.datetime.now().weekday())

        data = await state.get_data()

        data['day'] = datetime.datetime.now().weekday()
        data['type_of_week'] = get_week_type()
        schedule = db.get_next(data['group'], data['type_of_week'], data['day'],
                               datetime.datetime.now().hour, datetime.datetime.now().minute)

        await message.answer(f"{schedule}", parse_mode="HTML")
        await message.delete()


@dp.message_handler(commands=['time'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_time(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    data = await state.get_data()
    if 'group' not in data:
        await message.answer("Вам спершу необхідно обрати групу - /setgroup")

    else:
        await Info.type_of_week.set()
        state = dp.get_current().current_state()
        await state.update_data(type_of_week=get_week_type())

        await Info.day.set()
        state = dp.get_current().current_state()
        await state.update_data(day=datetime.datetime.now().weekday())

        data = await state.get_data()

        result = db.get_time(data['group'], data['type_of_week'], data['day'],
                             datetime.datetime.now().hour, datetime.datetime.now().minute)
        await message.answer(f"{result}", parse_mode="HTML")
        await message.delete()


@dp.message_handler(commands=['tomorrow', 'today'], state='*')
@dp.throttled(anti_spam, rate=1)
async def cmd_tomorrow_today(message: types.Message, state: FSMContext) -> None:
    await Info.group.set()
    data = await state.get_data()

    if 'group' not in data:
        await message.answer("Вам спершу необхідно обрати групу - /setgroup")

    else:
        await state.update_data(type_of_week=get_week_type())

        await Info.day.set()
        state = dp.get_current().current_state()
        await state.update_data(day=datetime.datetime.now().weekday())

        data = await state.get_data()

        if 'today' in message.text:
            ids, schedule = db.get_day_schedule(data['group'], data['type_of_week'], data['day'])
            await message.answer(f"<b>Розклад на сьогодні</b>: {schedule}", parse_mode="HTML")
        else:
            data['day'] += 1  # херняяяя
            ids, schedule = db.get_day_schedule(data['group'], data['type_of_week'], data['day'])
            await message.answer(f"<b>Розклад на завтра</b>: {schedule}", parse_mode="HTML")

        await message.delete()


@dp.callback_query_handler(text_contains="group:", state=Info.all_states)
async def callback_group(callback: types.CallbackQuery, state: FSMContext):
    if callback.data and callback.data.startswith("group:"):
        if "back" in callback.data:
            await callback.message.edit_text("Оберіть опцію...", reply_markup=ikb_wd)
        else:
            data = await state.get_data()
            if 'group' not in data or callback.data.split(':')[1] not in data.values():
                # await Info.group.set()
                state = dp.get_current().current_state()
                await state.update_data(group=callback.data.split(':')[1])

            data = await state.get_data()

            await callback.message.edit_text(f"Групу обрано - {data['group']}\n"
                                             f"Оберіть що бажаєте дізнатись: \n{HELP}",
                                             parse_mode="HTML")


@dp.callback_query_handler(text_contains="search:", state=Info.all_states)
async def callback_group(callback: types.CallbackQuery, state: FSMContext):
    if callback.data and callback.data.startswith("search:"):
        data = await state.get_data()
        if 'group' not in data:
            await callback.message.answer("Вам спершу необхідно обрати групу - /setgroup")

        await Info.type_of_week.set()
        state = dp.get_current().current_state()
        await state.update_data(type_of_week=get_week_type())

        data = await state.get_data()

        period = callback.data.split(':')[1]
        if period == "week":
            # print(data['group'], data['type_of_week'])
            schedule = db.get_week_schedule(data['group'], data['type_of_week'])
            await callback.message.edit_text(f"Поточний тиждень - {data['type_of_week']}\n"
                                             f"{schedule}", parse_mode="HTML",
                                             reply_markup=ikb_changeweek)

        if period == "day":
            await callback.message.edit_text(f"Поточний тиждень - {data['type_of_week']}\n"
                                             f"Оберіть день ...",
                                             reply_markup=ikb_days)


@dp.callback_query_handler(text_contains="changeweek", state=Info.all_states)
async def callback_week(callback: types.CallbackQuery, state: FSMContext):
    # data = await state.get_data()
    async with state.proxy() as data:
        data['type_of_week'] = "Парний" if data['type_of_week'] == "Непарний" else "Непарний"
        schedule = db.get_week_schedule(data['group'], data['type_of_week'])
        await callback.message.edit_text(f"Тиждень - {data['type_of_week']}\n"
                                         f"{schedule}", parse_mode="HTML",
                                         reply_markup=ikb_chooseday)


@dp.callback_query_handler(text_contains="day:", state=Info.all_states)
async def callback_day(callback: types.CallbackQuery, state: FSMContext):
    # await Info.day.set()
    # state = dp.get_current().current_state()
    # await state.update_data(day=int(callback.data.split(':')[1]))
    # await Info.type_of_week.set()
    # state = dp.get_current().current_state()
    # await state.update_data(type_of_week=get_week_type())
    #
    # data = await state.get_data()
    async with state.proxy() as data:
        data['day'] = int(callback.data.split(':')[1])
        data['type_of_week'] = get_week_type()
        # print(callback.data)
        if 'ch' in callback.data:
            data['type_of_week'] = "Парний" if data['type_of_week'] == "Непарний" else "Непарний"
            # print(data['group'], data['type_of_week'], data['day'])
            ids, schedule = db.get_day_schedule(data['group'], data['type_of_week'], data['day'])
            # print(schedule)
            await callback.message.edit_text(f"Поточний тиждень - {data['type_of_week']}\n"
                                             f"{schedule}", parse_mode="HTML",
                                             reply_markup=ikb_chooseday)
        else:
            #     data['type_of_week'] = "Парний" if data['type_of_week'] == "Непарний" else "Непарний"
            # print(data['group'], data['type_of_week'], data['day'])
            ids, schedule = db.get_day_schedule(data['group'], data['type_of_week'], data['day'])
            # print(schedule)
                # await callback.message.edit_text(f"Поточний тиждень - {data['type_of_week']}\n"
                #                                  f"{schedule}", parse_mode="HTML",
                #                                  reply_markup=ikb_chooseday)
            # schedule = db.get_day_schedule(data['group'], data['type_of_week'], data['day'])
            await callback.message.edit_text(f"Поточний тиждень - {data['type_of_week']}\n"
                                             f"{schedule}", parse_mode="HTML",
                                             reply_markup=ikb_days)

# -----------------------------ADMIN PART----------------------------


@dp.callback_query_handler(text_contains="check", state='*')
async def callback_check(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Перевірка збігів у розкладі...")
    db_data, result_classrooms = db.get_coincidence_classroom()
    if result_classrooms == "":
        await callback.message.answer("Збігів у кабінетах не виявлено! Групи розподілені по кабінетах правильно")
        db_data, result_lecturers = db.get_coincidence_lecturer()
        if result_lecturers == "":
            await callback.message.answer("Збігів у викладачів не виявлено! Викладачі розподілені по заняттях правильно")
        else:
            await callback.message.answer(result_lecturers)
            await state.set_state(Coincidence.all_states)
            async with state.proxy() as data:
                data['id'] = db_data[0]
                data['subject'] = db_data[9]
                data['sub_lec'] = db_data[10]
                data['class_num'] = db_data[1]
                data['day'] = db_data[4]
                data['type_of_week'] = db_data[5]
                # print(data)
                # print(await state.get_state())
            await callback.message.answer("Обрати ", reply_markup=ikb_change_lectsub)
    else:
        await Coincidence.group.set()
        async with state.proxy() as data:
            data['id'] = db_data[0]
            data['group'] = db_data[1]
            data['day'] = db_data[2]
            data['type_of_week'] = db_data[3]
            # print("WHATTTTTTTT" , data['type_of_week'])
            data['class_num'] = db_data[4]
            data['classroom'] = db_data[5]
        # await Coincidence.group.set()
        # await state.update_data(day=db_data[1])
        # await Coincidence.classroom.set()
        # await state.update_data(classroom=db_data[5])
        # await Coincidence.day.set()
        # await state.update_data(day=db_data[2])
        # await Coincidence.type_of_week.set()
        # await state.update_data(type_of_week=db_data[3])
        # await Coincidence.class_num.set()
        # await state.update_data(class_num=db_data[4])
        # await Coincidence.id.set()
        # await state.update_data(id=db_data[0])

        await callback.message.answer(f"Виявлено збіг: {result_classrooms}")
        await Coincidence.classroom.set()
        await callback.message.answer("Введіть інший кабінет для групи: ")


@dp.callback_query_handler(text_contains="change_lectsub:", state='*')
async def change_lectsub(callback: types.CallbackQuery, state: FSMContext):
    # print("hello")
    # await Coincidence.save_ids.set()
    # await state.set_state(Coincidence.save_ids)
    print(await state.get_state())
    async with state.proxy() as data:
        if "setlecturer" in callback.data:
            lecturers_by_subject = db.get_lecturers(data['class_num'], data['subject'],
                                                    data['day'], data['type_of_week'], data['sub_lec'])
            res = ""
            data['save_ids'] = dict()
            i = 0
            for ls in lecturers_by_subject:
                i += 1
                res += f"{i}. {ls[1]} {ls[2]} {ls[3]}\n"
                data['save_ids'][i] = ls[0]
            data['max_lecturers'] = i
            # print(res)
            if not res:
                await callback.message.answer("Немає вільних викладачів на цей предмет.")
                callback.data = "setsubject"
            else:
                await callback.message.answer(res)
                await Coincidence.lecturer.set()
                # ............
        if "setsubject" in callback.data:
            sub_lec = db.get_sub_lec(data['class_num'], data['day'], data['type_of_week'])
            # print(data['type_of_week'])
            # print(sub_lec)
            # res = []
            # i = 0
            # for sl in sub_lec:
            #     res.append(f"{sl[0]}. <b>{sl[2]}</b>({sl[1]})\n"
            #                f" - <em>{sl[3]} {sl[4]} {sl[5]}</em>\n")
            res = []
            data['save_ids'] = dict()
            i = 0
            for sl in sub_lec:
                i += 1
                res.append( f"{i}. <b>{sl[2]}</b>({sl[1]})\n"\
                            f" - <em>{sl[3]} {sl[4]} {sl[5]}</em>\n")
                data['save_ids'][i] = sl[0]
            data['max_lecturers'] = i
            await callback.message.answer(f"Оберіть викладача та предмет: ")
            # print(sub_lec)
            result = ""
            for i in range(len(res)):
                if i < len(res) // 7 or i > len(res) // 7 or i > 2 * len(res) // 7 or i > 3 * len(res) // 7\
                        or i > 4 * len(res) // 7 or i > 5 * len(res) // 7 or i > 6 * len(res) // 7:
                    result += res[i]
                if i == len(res) // 7 or i == 2 * len(res) // 7 or i == 3 * len(res) // 7 or i == 4 * len(res) // 7\
                        or i == 5 * len(res) // 7 or i == 6 * len(res) // 7 or i == len(res) - 1:
                    await callback.message.answer(result, parse_mode="HTML")
                    print(result)
                    result = ""
            await Coincidence.subject.set()


@dp.message_handler(state=Coincidence.lecturer)
async def check_lec(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Не правильно задані дані, повинен бути номер "
                            "викладача, введіть ще раз")
    else:
        message.text = int(message.text)
        async with state.proxy() as data:
            if message.text < 0 or message.text > data['max_lecturers']:
                await message.reply("Не правильно задані дані, повинен бути номер "
                                    "викладача, введіть ще раз")
            else:
                check = db.check_sub_lec_id(message.text)
                if check:
                    async with state.proxy() as data:
                        data['lecturer'] = data['save_ids'][int(message.text)]
                        set = db.set_lec_sub(data['id'], data['lecturer'])
                        if set:
                            await message.answer("Викладача успішно змінено")
                            await state.finish()
                        else:
                            await message.answer("Щось пішло не так")
                else:
                    await message.answer("Не правильний номер, спробуйте ще")



# @dp.message_handler(state=Coincidence.lecturer)
# async def check_set_lecturer(message: types.Message, state: FSMContext):
#     check = db.check_sub_lec_id(message.text)
#     if check:
#         async with state.proxy() as data:
#             data['lecturer'] = data['save_ids'][message.text]
#             set = db.set_lec_sub(data['id'], data['lecturer'])
#             if set:
#                 await message.answer("Викладача успішно змінено")
#                 await state.finish()
#             else:
#                 await message.answer("Щось пішло не так")
#     else:
#         await message.answer("Не правильний номер, спробуйте ще")
    # async with state.proxy() as data:
    #     try:
    #         message.text = int(message.text)
    #         if message.text > 0 and message.text < data['max_lecturers']:
    #             data['lecturer'] = data['save_ids'][message.text]
    #             set = db.set_lec_sub(data['id'], data['lecturer'])
    #             if set:
    #                 await message.answer("Викладача успішно змінено")
    #             else:
    #                 await message.answer("Щось пішло не так")
    #     except (TypeError, ValueError):
    #         await message.reply(f"Ви повинні ввести ціле число в межах від 1 до {data['max_lecturers']}")


@dp.message_handler(state=Coincidence.subject)
async def check_sub_lec(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Не правильно задані дані, повинен бути номер "
                            "комбінації викладача та предмета, введіть ще раз")
    else:
        # print(await state.get_state())
        async with state.proxy() as data:
            print(data)
            message.text = int(message.text)
            if message.text < 0 or message.text > data['max_lecturers']:
                await message.reply("Не правильно задані дані, повинен бути номер "
                                    "комбінації викладача та предмета, введіть ще раз")
            else:
                check = db.check_sub_lec_id(message.text)
                print(check)
                if check:
                    lec_sub = message.text
                    print(lec_sub)

                    async with state.proxy() as data:
                        print(data['id'])
                        change = db.set_lec_sub(data['id'], lec_sub)
                        if change:
                            await message.answer("Успішно змінено предмет та викладача!")
                            await state.finish()
                        else:
                            await message.answer("Цей викладач вже зайнятий")
                else:
                    await message.answer("Неправильний номер, спробуйте ще")
                #--------------------


# @dp.message_handler(state=Coincidence.subject)
# async def set_subject(message: types.Message, state: FSMContext):
#     print("HELLO")
#     check = db.check_sub_lec_id(message.text)
#     print(check)
#     if check:
#         lec_sub = message.text
#         print(lec_sub)
#
#         async with state.proxy() as data:
#             print(data['id'])
#             change = db.set_lec_sub(data['id'], lec_sub)
#             if change:
#                 await message.answer("Успішно змінено предмет та викладача!")
#                 await state.finish()
#             else:
#                 await message.answer("Цей викладач вже зайнятий")
#     else:
#         await message.answer("Неправильний номер, спробуйте ще")


@dp.message_handler(lambda message: "Каб" not in message.text and "Ауд" not in message.text
                    and "Онлайн" not in message.text, state=Coincidence.classroom)
async def check_classroom(message: types.Message):
    await message.reply("Не правильно задані дані, повинно містити 'Каб.*', 'Ауд.*' чи 'Онлайн', введіть ще раз")


@dp.message_handler(state=Coincidence.classroom)
async def check_if_exists(message: types.Message, state: FSMContext):
    data = await state.get_data()
    check = db.check_new_classroom(message.text, data['day'], data['class_num'], data['type_of_week'])
    # await message.reply("Цей кабінет вільний!" if not check else "Оберіть інший кабінет, цей зайнято")
    if not check:
        await state.update_data(classroom=message.text)
        data = await state.get_data()
        print(data)
        change = db.change_classroom(data['id'], data['classroom'])
        print(change)
        await message.answer("Кабінет змінено!" if change else "Щось пішло не так...")
        await state.finish()
    else:
        await message.reply("Оберіть інший кабінет, цей зайнято")


@dp.callback_query_handler(text_contains="addclass", state='*')
async def callback_change(callback: types.CallbackQuery, state: FSMContext):
    if "no" in callback.data:
        await state.finish()
        await callback.message.answer("Зміну/додавання скасовано.")

    if "frommodify" in callback.data:
        await ModifyClass.class_num.set()
        async with state.proxy() as data:
            print(data)
            if 'group' in data and 'type_of_week' in data and 'day' in data:
                group = data['group']
                type_of_week = data['type_of_week']
                day = data['day']
                await AddClass.group.set()
                await state.update_data(group=group)
                await AddClass.type_of_week.set()
                await state.update_data(type_of_week=type_of_week)
                await AddClass.day.set()
                await state.update_data(day=day)
                await callback.message.answer("Введіть номер заняття, яке бажаєте додати:")
                await AddClass.class_num.set()
    else:
        await callback.message.answer("Оберіть групу якій хочете додати предмет", reply_markup=ikb_group_add)


@dp.callback_query_handler(text_contains="add:", state='*')
async def callback_add(callback: types.CallbackQuery, state: FSMContext):
    if callback.data and callback.data.startswith("add:"):
        await AddClass.group.set()
        await state.update_data(group=callback.data.split(':')[1])
        data = await state.get_data()
        await callback.message.edit_text(f"Групу обрано - {data['group']}\n"
                                         f"Оберіть тиждень",
                                         reply_markup=ikb_chooseweek)
        await AddClass.type_of_week.set()


@dp.callback_query_handler(text_contains="week:", state=AddClass.type_of_week)
async def callback_setweek(callback: types.CallbackQuery, state: FSMContext):
    if callback.data and callback.data.startswith("week:"):
        week = callback.data.split(':')[1]
        await state.update_data(type_of_week=week)
        data = await state.get_data()
        await callback.message.edit_text(f"Тиждень обрано - {data['type_of_week']}\n"
                                         f"Оберіть день:",
                                         reply_markup=ikb_setday)
        await AddClass.day.set()


@dp.callback_query_handler(text_contains="setday:", state=AddClass.day)
async def callback_setday(callback: types.CallbackQuery, state: FSMContext):
    if callback.data and callback.data.startswith("setday:"):
        async with state.proxy() as data:
            day = callback.data.split(':')[1]
            # await state.update_data(day=day)
            # data = await state.get_data()
            days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            data['day'] = day
            ids, day_schedule = db.get_day_schedule(data['group'], data['type_of_week'], int(data['day']))
            if ids:
                data['setted_classes'] = dict(ids)
            await callback.message.edit_text(f"День обрано - {days[int(day)]}\n"
                                             f"Розклад на цей день у групі {data['group']}:"
                                             f"{day_schedule}\n", parse_mode="HTML")
            await callback.message.answer("Введіть номер заняття, яке бажаєте додати:")
            await AddClass.class_num.set()


@dp.message_handler(state=AddClass.class_num)
async def check_set_class(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Неправильно вказаний номер заняття для додавання, спробуйте ще")
    else:
        async with state.proxy() as data:
            if 'setted_classes' in data:
                if int(message.text) not in data['setted_classes'] and 0 < int(message.text) < 7:
                    data['class_num'] = int(message.text)
                    await message.answer(f"Час заняття обрано - {data['class_num']}\n"
                                         f"Введіть класну кімнату:")
                    await AddClass.classroom.set()
                else:
                    # setted_classes = data['setted_classes']
                    # print("ADDCLASS", await state.get_data())
                    # await ModifyClass.class_num.set()
                    # await state.update_data(class_num=setted_classes[int(message.text)])
                    data['class_num'] = data['setted_classes'][int(message.text)]
                    await message.reply("Неправильно вказаний номер заняття для додавання, "
                                        "можливо ви бажаєте модифікувати заняття?", reply_markup=ikb_modify_from_add)
            elif 'setted_classes' not in data and 0 < int(message.text) < 7:
                data['class_num'] = int(message.text)
                await message.answer(f"Час заняття обрано - {data['class_num']}\n"
                                     f"Введіть класну кімнату:")
                await AddClass.classroom.set()
            else:
                await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")

    # if callback.data and callback.data.startswith("class_num:"):
    #     class_num = callback.data.split(':')[1]
    #     await state.update_data(class_num=class_num)
    #     data = await state.get_data()
    #     await callback.message.edit_text(f"Час заняття обрано - {data['class_num']}\n"
    #                                      f"Введіть класну кімнату:", reply_markup=ikb_go_back_classnum)
    #     await AddClass.classroom.set()


@dp.message_handler(lambda message: "Каб" not in message.text and "Ауд" not in message.text
                    and "Онлайн" not in message.text, state=AddClass.classroom)
async def check_classroom(message: types.Message):
    await message.reply("Не правильно задані дані, повинно містити 'Каб.*', 'Ауд.*' чи 'Онлайн', введіть ще раз")


@dp.message_handler(state=AddClass.classroom)
async def set_classroom(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        check = db.check_new_classroom(message.text, data['day'], data['class_num'], data['type_of_week'])
        # await message.reply("Цей кабінет вільний!" if not check else "Оберіть інший кабінет, цей зайнято")
        if not check:
            # await state.update_data(classroom=message.text)
            # data = await state.get_data()
            data['classroom'] = message.text
            sub_lec = db.get_sub_lec(data['class_num'], data['day'], data['type_of_week'])
            await message.answer(f"Кабінет обрано! - {data['classroom']}")
            res = []
            data['save_ids'] = dict()
            i = 0
            for sl in sub_lec:
                i += 1
                res.append(f"{i}. <b>{sl[2]}</b>({sl[1]})\n"
                           f" - <em>{sl[3]} {sl[4]} {sl[5]}</em>\n")
                data['save_ids'][i] = sl[0]
            data['max_lecturers'] = i
            await message.answer(f"Оберіть викладача та предмет: ")
            # print(sub_lec)
            result = ""
            for i in range(len(res)):
                if i < len(res) // 7 or i > len(res) // 7 or i > 2 * len(res) // 7 or i > 3 * len(res) // 7\
                        or i > 4 * len(res) // 7 or i > 5 * len(res) // 7 or i > 6 * len(res) // 7:
                    result += res[i]
                if i == len(res) // 7 or i == 2 * len(res) // 7 or i == 3 * len(res) // 7 \
                        or i == 4 * len(res) // 7 or i == 5 * len(res) // 7 or i == 6 * len(res) // 7 or i == len(res) - 1 :
                    await message.answer(result, parse_mode="HTML")
                    # print(result)
                    result = ""
            await AddClass.sub_lec.set()
        else:
            await message.reply("Оберіть інший кабінет, цей зайнято")


@dp.message_handler(lambda message: not message.text.isdigit(), state=AddClass.sub_lec)
async def check_sub_lec(message: types.Message):
    await message.reply("Не правильно задані дані, повинен бути номер "
                        "комбінації викладача та предмета, введіть ще раз")


@dp.message_handler(state=AddClass.sub_lec)
async def set_sub_lec(message: types.Message, state: FSMContext):

    check = db.check_sub_lec_id(message.text)
    if check:
        async with state.proxy() as data:
            data['sub_lec'] = data['save_ids'][int(message.text)]

            # check if classroom is empty in that class number
            # check_classroom = db.check_new_classroom(message.text, data['day'],
            #                                          data['class_num'], data['type_of_week'])
            check_class_num = db.check_class_num(data['group'], data['type_of_week'], data['day'], data['class_num'])
            if not check_class_num:
                add = db.add_class(data['group'], data['type_of_week'], data['day'], data['class_num'],
                                   data['classroom'], data['sub_lec'])
                if add:
                    await message.answer("Заняття додане у розклад!")
                    await state.finish()
            else:
                await message.answer(f"У цієї групи вже є заняття під номером {data['class_num']}\n"
                                     f"{check_class_num}",
                                     reply_markup=ikb_choose_to_change, parse_mode="HTML")
    else:
        await AddClass.classroom.set()


@dp.callback_query_handler(text_contains="no", state=AddClass.sub_lec)
async def callback_cancel_adding(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("Заміна успішно скасована.")


@dp.callback_query_handler(text_contains="change_class", state=AddClass.sub_lec)
async def callback_update_class(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    change = db.change_by_id(data['group'], data['type_of_week'], data['day'], data['class_num'],
                             data['classroom'], data['sub_lec'])
    if change:
        await callback.message.edit_text("Заміна успішно проведена!")
        await state.finish()
    else:
        await callback.message.edit_text("Щось пішло не так, заміна не проведена, спробуйте ще")
        await state.finish()


@dp.callback_query_handler(text_contains="modifyclass", state='*')
async def callback_modify_class(callback: types.CallbackQuery, state: FSMContext):
    # print(await state.get_state())
    # await state.set_state(ModifyClass.all_states)
    # async with state.proxy() as data:
    #     if 'group' not in data:
    # await ModifyClass.group.set()
    # if not await state.get_data():
    if "fromadd" in callback.data:
        await AddClass.class_num.set()
        async with state.proxy() as data:
            if 'group' in data and 'type_of_week' in data and 'day' in data:
                group = data['group']
                type_of_week = data['type_of_week']
                day = data['day']
                class_num = data['class_num']
                await state.finish()
                await ModifyClass.group.set()
                await state.update_data(group=group)
                await ModifyClass.type_of_week.set()
                await state.update_data(type_of_week=type_of_week)
                await ModifyClass.day.set()
                await state.update_data(day=day)
                await ModifyClass.class_num.set()
                await state.update_data(class_num=class_num)
                await state.get_state()
                # await callback.message.answer("Введіть номер заняття, яке бажаєте змінити:")
                # await ModifyClass.class_num.set()
                await callback.message.answer("Що бажаєте модифікувати?", reply_markup=ikb_which_change)
    elif callback.data == "modifyclass":
        await callback.message.edit_text("Оберіть групу", reply_markup=ikb_group_modify)
    elif "group" in callback.data:
        # await ModifyClass.group.set()
        # data['group'] = callback.data.split(':')[1]
        if callback.data.split(':')[1]:
            await ModifyClass.group.set()
            await state.update_data(group=callback.data.split(':')[1])
        # print(await state.get_data())
        await callback.message.edit_text("Оберіть тиждень", reply_markup=ikb_week_modify)
    # else:
    #     await callback.message.answer("Оберіть групу", reply_markup=ikb_group_modify)
    elif "week" in callback.data:
        print(callback.data)
        await ModifyClass.type_of_week.set()
        await state.update_data(type_of_week=callback.data.split(':')[1])
        # data['type_of_week'] = callback.data.split(':')[1]
        await callback.message.edit_text("Оберіть день", reply_markup=ikb_day_modify)
    elif "day" in callback.data:
        await ModifyClass.day.set()
        await state.update_data(day=callback.data.split(':')[1])
        # data['day'] = callback.data.split(':')[1]
        # print(data['day'])
        async with state.proxy() as data:
            ids, day_schedule = db.get_day_schedule(data['group'], data['type_of_week'], int(data['day']))
            await ModifyClass.available_classes.set()
            if ids:
                await state.update_data(available_classes=dict(ids))
                print(await state.get_data())
            # data['available_classes'] = list(ids.keys())
                await callback.message.answer(day_schedule, parse_mode="HTML")
                await ModifyClass.class_num.set()
                await callback.message.answer("Введіть номер заняття, яке хочете змінити:")
            else:
                await callback.message.answer(day_schedule, parse_mode="HTML")
                # await callback.message.answer("Додати заняття?")
                await callback.message.answer("Додати заняття?", reply_markup=ikb_add_from_modify)

    elif "no" in callback.data:
        await state.finish()
        await callback.message.answer("Зміну/додавання скасовано.")

    elif "sublect" in callback.data:
        async with state.proxy() as data:
            # await state.get_data()
            sub_lec = db.get_sub_lec(data['class_num'], data['day'], data['type_of_week'])
            # await callback.message.answer("Оберіть викладача:")
            # print(sub_lec)
            # res = ""
            # for i in range(len(sub_lec)):
            #     if i < len(sub_lec) // 4 or i > len(sub_lec) // 4 or i > 2 * len(sub_lec) // 4:
            #         res += sub_lec[i]
            #     if i == len(sub_lec) // 4 or i == 2 * len(sub_lec) // 4 or i == len(sub_lec) - 1:
            #         await callback.message.answer(res, parse_mode="HTML")
            #         res = ""
            res = []
            data['save_ids'] = dict()
            i = 0
            for sl in sub_lec:
                i += 1
                res.append(f"{i}. <b>{sl[2]}</b>({sl[1]})\n" 
                           f" - <em>{sl[3]} {sl[4]} {sl[5]}</em>\n")
                data['save_ids'][i] = sl[0]
            data['max_lecturers'] = i
            await callback.message.answer(f"Оберіть викладача та предмет: ")
            # print(sub_lec)
            result = ""
            for i in range(len(res)):
                if i < len(res) // 7 or i > len(res) // 7 or i > 2 * len(res) // 7 or i > 3 * len(res) // 7\
                        or i > 4 * len(res) // 7 or i > 5 * len(res) // 7 or i > 6 * len(res) // 7:
                    result += res[i]
                if i == len(res) // 7 or i == 2 * len(res) // 7 or i == 3 * len(res) // 7 or\
                        i == 4 * len(res) // 7 or i == 5 * len(res) // 7 or i == 6 * len(res) // 7 or i == len(res) - 1 :
                    await callback.message.answer(result, parse_mode="HTML")
                    result = ""
            await ModifyClass.sub_lec.set()
    elif "classroom" in callback.data:
        await callback.message.answer("Введіть кабінет:")
        await ModifyClass.classroom.set()


@dp.message_handler(state=ModifyClass.class_num)
async def check_classnum(message: types.Message, state: FSMContext):
    # async with state.proxy() as data:
        # if 'class_num' in data:
            # class_num = data['class_num']
            # data['class_num'] = data['available_classes'][class_num]

    if not message.text.isdigit():
        await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")
    else:
        async with state.proxy() as data:
            # if int(message.text) <= 0 or int(message.text) > 6:
            #     await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")
            if int(message.text) not in data['available_classes']:
                await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")
            else:
                await state.update_data(class_num=data['available_classes'][int(message.text)])
                print(data['available_classes'][int(message.text)])
                await message.answer("Бажаєте змінити викладача/предмет чи кабінет?", reply_markup=ikb_which_change)


# @dp.message_handler(state=ModifyClass.class_num)
# async def set_classnum(message: types.Message, state: FSMContext):
#     await ModifyClass.class_num.set()
#     await state.update_data(class_num=message.text)
#     print(state.get_data())
#     await message.answer("Бажаєте змінити викладача/предмет чи кабінет?", reply_markup=ikb_which_change)
#


# @dp.message_handler(lambda message: not message.text.isdigit(), state=ModifyClass.sub_lec)
# async def check_sub_lec(message: types.Message):
#     await message.reply("Не правильно задані дані, повинен бути номер "
#                         "комбінації викладача та предмета, введіть ще раз")


@dp.message_handler(state=ModifyClass.sub_lec)
async def set_sub_lec(message: types.Message, state: FSMContext):
    # check = db.check_sub_lec_id(message.text)
    # if check:
    #     await state.update_data(sub_lec=message.text)
    #     data = await state.get_data()
    # else:
    #     await message.reply("Не правильно задані дані, спробуйте ще.")
    if not message.text.isdigit():
        await message.reply("Не правильно задані дані, повинен бути номер "
                            "викладача, введіть ще раз")
    else:
        message.text = int(message.text)
        async with state.proxy() as data:
            if message.text < 0 or message.text > data['max_lecturers']:
                await message.reply("Не правильно задані дані, повинен бути номер "
                                    "викладача, введіть ще раз")
            else:
                check = db.check_sub_lec_id(message.text)
                if check:
                    async with state.proxy() as data:
                        data['lecturer'] = data['save_ids'][message.text]
                        # print(data['save_ids'])
                        set = db.set_lec_sub(data['class_num'], data['lecturer'])
                        if set:
                            await message.answer("Успішно змінено")
                            await state.reset_data()
                        else:
                            await message.answer("Ви не внесли зміни, цей предмет і був у розкладі")
                            await state.reset_data()

                else:
                    await message.answer("Не правильний номер, спробуйте ще")


@dp.message_handler(lambda message: "Каб" not in message.text and "Ауд" not in message.text
                    and "Онлайн" not in message.text, state=ModifyClass.classroom)
async def check_classroom(message: types.Message):
    await message.reply("Не правильно задані дані, повинно містити 'Каб.*', 'Ауд.*' чи 'Онлайн', введіть ще раз")


@dp.message_handler(state=ModifyClass.classroom)
async def set_classroom(message: types.Message, state: FSMContext):
    data = await state.get_data()
    check = db.check_new_classroom(message.text, data['day'], data['class_num'], data['type_of_week'])
    # await message.reply("Цей кабінет вільний!" if not check else "Оберіть інший кабінет, цей зайнято")
    if not check:
        await state.update_data(classroom=message.text)
        data = await state.get_data()
        await message.answer(f"Кабінет обрано! - {data['classroom']}")
        change = db.change_classroom(data['class_num'], data['classroom'])
        if change:
            await message.answer(f"Кабінет змінено!")
            await state.finish()
        else:
            await message.reply("Щось пішло не так")
    else:
        await message.reply("Оберіть інший кабінет, цей зайнято")


@dp.callback_query_handler(text_contains="deleteclass", state='*')
async def callback_delete_class(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "deleteclass":
        await callback.message.edit_text("Оберіть групу для видалення заняття:", reply_markup=ikb_group_delete)
    elif "group" in callback.data:
        if callback.data.split(':')[1]:
            await DeleteClass.group.set()
            await state.update_data(group=callback.data.split(':')[1])
        await callback.message.edit_text("Оберіть тиждень", reply_markup=ikb_week_delete)
    elif "week" in callback.data:
        print(callback.data)
        await DeleteClass.type_of_week.set()
        await state.update_data(type_of_week=callback.data.split(':')[1])
        await callback.message.edit_text("Оберіть день", reply_markup=ikb_day_delete)
    elif "day" in callback.data:
        await DeleteClass.day.set()
        await state.update_data(day=callback.data.split(':')[1])
        async with state.proxy() as data:
            ids, day_schedule = db.get_day_schedule(data['group'], data['type_of_week'], int(data['day']))
            await DeleteClass.available_classes.set()
            if ids:
                await state.update_data(available_classes=dict(ids))
                print(await state.get_data())
                # data['available_classes'] = list(ids.keys())
                await callback.message.answer(day_schedule, parse_mode="HTML")
                await DeleteClass.class_num.set()
                await callback.message.answer("Введіть номер заняття, яке хочете видалити:")
            else:
                await callback.message.answer(day_schedule, parse_mode="HTML")
                await state.finish()  # ?


@dp.message_handler(state=DeleteClass.class_num)
async def check_classnum(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")
    else:
        async with state.proxy() as data:
            if int(message.text) not in data['available_classes']:
                await message.reply("Неправильно вказаний номер заняття для зміни, спробуйте ще")
            else:
                # await DeleteClass.class_num.set()
                data['class_num'] = data['available_classes'][int(message.text)]
                # await state.get_data()
                # print(data['available_classes'][int(message.text)])
                delete = db.delete_class(data['class_num'])
                if delete:
                    await message.answer("Заняття успішно видалено!")
                else:
                    await message.answer("Заняття не видалено, щось пішло не так")


@dp.callback_query_handler(text_contains="setmoderator", state='*')
async def callback_set_moderator(callback: types.CallbackQuery, state: FSMContext):
    await SetAdmin.id.set()
    await callback.message.answer("Введіть username користувача у телеграм, якого хочете зробити адміном:")


@dp.message_handler(lambda message: "@" not in message.text, state=SetAdmin.id)
async def check_setmoderator(message: types.Message, state: FSMContext):
    await message.reply("Не правильний формат, спробуйте ще раз із знаком '@'")


# @dp.message_handler(state=SetAdmin.id)
# async def set_moderator(message: types.Message, state: FSMContext):
#     username = message.text
#     id = username.id
#     .......

@dp.message_handler(state=SetAdmin.id)
async def set_moderator(message: types.Message, state: FSMContext):
    username = message.text
    global moderators
    moderators.append(username)
    await message.answer("Модератор доданий!")


# --------------------------------------------------------------------

@dp.message_handler()
@dp.throttled(anti_spam, rate=0.5)
async def clean(message: types.Message):
    await message.reply("Дана команда не підтримується, введіть /start щоб оновити, /help для списку команд")
    await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
