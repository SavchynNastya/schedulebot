from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db import ScheduleDB


db = ScheduleDB()

# button_for_cancel = KeyboardButton('/cancel')
# button_after_cancel = KeyboardButton('/start')
# red_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_for_cancel)
# red_2 = ReplyKeyboardMarkup(resize_keyboard=True).add(button_after_cancel)


ikb_group = InlineKeyboardMarkup(resize_keyboard=True)
groups = db.get_groups()
for group in groups:
    ib = InlineKeyboardButton(f"{group}", callback_data=f"group:{group}")
    ikb_group.add(ib)

# ikb_group_add = InlineKeyboardMarkup(resize_keyboard=True)
# groups = db.get_groups()
# for group in groups:
#     ib = InlineKeyboardButton(f"{group}", callback_data=f"add:{group}")
#     ikb_group_add.add(ib)
# ikb_group.add(InlineKeyboardButton("↩️Назад", callback_data=''))

# ikb_group = InlineKeyboardMarkup(resize_keyboard=True)
# for i in range(len(groups), 3):
#     for j in range(len(groups) // 3 + len(groups) % 3):
#         try:
#             ikb_group.add(InlineKeyboardButton(f"{groups[i]}", callback_data=f"group:{groups[i]}"),
#                           InlineKeyboardButton(f"{groups[i+1]}", callback_data=f"group:{groups[i+1]}"),
#                           InlineKeyboardButton(f"{groups[i+2]}", callback_data=f"group:{groups[i+2]}"))
#             print("added")
#         except IndexError:
#             break

# groups = [groups[i * 3:(i + 1) * 3] for i in range((len(groups) + 3 - 1) // 3)]
# for group_set in groups:
#     set_len = len(group_set)
#     for i in range(set_len):

# після вибору групи для вибору тижня чи дня тижня
ikb_wd = InlineKeyboardMarkup(resize_keyboard=True)
ib1 = InlineKeyboardButton("Тиждень", callback_data='search:week')
ib2 = InlineKeyboardButton("Конкретний день", callback_data='search:day')
ikb_wd.add(ib1)
ikb_wd.add(ib2)
ikb_wd.add(InlineKeyboardButton('↩️Назад', callback_data='group:'))

ikb_days = InlineKeyboardMarkup()
b1 = InlineKeyboardButton("Понеділок", callback_data='day:0')
b2 = InlineKeyboardButton("Вівторок", callback_data='day:1')
b3 = InlineKeyboardButton("Середа", callback_data='day:2')
b4 = InlineKeyboardButton("Четвер", callback_data='day:3')
b5 = InlineKeyboardButton("П'ятниця", callback_data="day:4")
b6 = InlineKeyboardButton("Субота", callback_data='day:5')
ikb_days.add(b1, b2, b3)
ikb_days.add(b4, b5, b6)
ikb_days.add(InlineKeyboardButton("↩️Назад", callback_data='group:back'))


ikb_changeweek = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Глянути інший тиждень', callback_data='changeweek')],
    [InlineKeyboardButton('↩️Назад', callback_data='group:back')]
])

# ---------------------------------ADMIN PART---------------------------------------
ikb_setday = InlineKeyboardMarkup()
b1 = InlineKeyboardButton("Понеділок", callback_data='setday:0')
b2 = InlineKeyboardButton("Вівторок", callback_data='setday:1')
b3 = InlineKeyboardButton("Середа", callback_data='setday:2')
b4 = InlineKeyboardButton("Четвер", callback_data='setday:3')
b5 = InlineKeyboardButton("П'ятниця", callback_data="setday:4")
b6 = InlineKeyboardButton("Субота", callback_data='setday:5')
ikb_setday.add(b1, b2, b3)
ikb_setday.add(b4, b5, b6)
ikb_setday.add(InlineKeyboardButton("↩️Назад", callback_data='add:'))

ikb_chooseweek = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Парний', callback_data='week:Парний')],
    [InlineKeyboardButton('Непарний', callback_data='week:Непарний')],
    [InlineKeyboardButton('↩️Назад', callback_data='addclass')]
])

ikb_chooseday = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Понеділок", callback_data='day:0:ch'),
     InlineKeyboardButton("Вівторок", callback_data='day:1:ch'),
     InlineKeyboardButton("Середа", callback_data='day:2:ch')],
    [InlineKeyboardButton("Четвер", callback_data='day:3:ch'),
     InlineKeyboardButton("П'ятниця", callback_data="day:4:ch"),
     InlineKeyboardButton("Субота", callback_data='day:5:ch')],
    [InlineKeyboardButton('↩️Назад', callback_data='group:back')]
])

ikb_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Перевірити коректність розкладу", callback_data='check')],
    [InlineKeyboardButton("Додати заняття в розклад", callback_data='addclass')],
    [InlineKeyboardButton("Змінити заняття в розкладі", callback_data='modifyclass')],
    [InlineKeyboardButton("Видалити заняття", callback_data='deleteclass')],
    [InlineKeyboardButton("Додати адміністратора", callback_data='setmoderator')]
])

ikb_group_add = InlineKeyboardMarkup(resize_keyboard=True)
groups = db.get_groups()
for group in groups:
    ib = InlineKeyboardButton(f"{group}", callback_data=f"add:{group}")
    ikb_group_add.add(ib)

ikb_setclass = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("1", callback_data='class_num:1'),
     InlineKeyboardButton("2", callback_data='class_num:2'),
     InlineKeyboardButton("3", callback_data='class_num:3')],
    [InlineKeyboardButton("4", callback_data='class_num:4'),
     InlineKeyboardButton("5", callback_data='class_num:5'),
     InlineKeyboardButton("6", callback_data='class_num:6')],
    [InlineKeyboardButton("↩️Назад", callback_data='setday:')],
])

ikb_choose_to_change = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Не змінювати", callback_data='no')],
    [InlineKeyboardButton("Змінити", callback_data='change_class')]
])

ikb_go_back_classnum = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("↩️Назад", callback_data='setday:')],
])

ikb_change_lectsub = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Іншого викладача", callback_data='change_lectsub:setlecturer')],
    [InlineKeyboardButton("Інший предмет", callback_data='change_lectsub:setsubject')],
])

ikb_group_modify = InlineKeyboardMarkup(resize_keyboard=True)
groups = db.get_groups()
for group in groups:
    ib = InlineKeyboardButton(f"{group}", callback_data=f"modifyclass_group:{group}")
    ikb_group_modify.add(ib)

ikb_week_modify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Парний', callback_data='modifyclass_week:Парний')],
    [InlineKeyboardButton('Непарний', callback_data='modifyclass_week:Непарний')],
    [InlineKeyboardButton('↩️Назад', callback_data='modifyclass')]
])

ikb_day_modify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Понеділок", callback_data='modifyclass_day:0'),
     InlineKeyboardButton("Вівторок", callback_data='modifyclass_day:1'),
     InlineKeyboardButton("Середа", callback_data='modifyclass_day:2')],
    [InlineKeyboardButton("Четвер", callback_data='modifyclass_day:3'),
     InlineKeyboardButton("П'ятниця", callback_data="modifyclass_day:4"),
     InlineKeyboardButton("Субота", callback_data='modifyclass_day:5')],
    [InlineKeyboardButton('↩️Назад', callback_data='modifyclass_group:')]
])

ikb_which_change = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Викладача/предмет", callback_data='modifyclass_sublect')],
    [InlineKeyboardButton("Кабінет/аудиторію", callback_data='modifyclass_classroom')],
    # [InlineKeyboardButton('↩️Назад', callback_data='modifyclass_group:')]
])

ikb_group_delete = InlineKeyboardMarkup(resize_keyboard=True)
groups = db.get_groups()
for group in groups:
    ib = InlineKeyboardButton(f"{group}", callback_data=f"deleteclass_group:{group}")
    ikb_group_delete.add(ib)


ikb_week_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Парний', callback_data='deleteclass_week:Парний')],
    [InlineKeyboardButton('Непарний', callback_data='deleteclass_week:Непарний')],
    [InlineKeyboardButton('↩️Назад', callback_data='deleteclass')]
])

ikb_day_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Понеділок", callback_data='deleteclass_day:0'),
     InlineKeyboardButton("Вівторок", callback_data='deleteclass_day:1'),
     InlineKeyboardButton("Середа", callback_data='deleteclass_day:2')],
    [InlineKeyboardButton("Четвер", callback_data='deleteclass_day:3'),
     InlineKeyboardButton("П'ятниця", callback_data="deleteclass_day:4"),
     InlineKeyboardButton("Субота", callback_data='deleteclass_day:5')],
    [InlineKeyboardButton('↩️Назад', callback_data='deleteclass_group:')]
])

ikb_add_class = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Так", callback_data='addclass')],
    [InlineKeyboardButton("Ні", callback_data='modifyclass_no')]
])

ikb_modify_class = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Так", callback_data='modifyclass')],
    [InlineKeyboardButton("Ні", callback_data='addclass_no')]
])

ikb_modify_from_add = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Так", callback_data='modifyclass_fromadd')],
    [InlineKeyboardButton("Ні", callback_data='modifyclass_no')]
])

ikb_add_from_modify = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("Так", callback_data='addclass_frommodify')],
    [InlineKeyboardButton("Ні", callback_data='addclass_no')]
])

# ---------------------------------ADMIN PART---------------------------------------




