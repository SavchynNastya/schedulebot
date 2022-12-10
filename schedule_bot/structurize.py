def structurize(schedule, num_of_class):
    if num_of_class in schedule:
        if schedule[num_of_class] == "---":
            return f"{num_of_class}. ---\n"
        return f"{num_of_class}. {schedule[num_of_class]['subject']}\n" \
               f"   {schedule[num_of_class]['type']}📝\n" \
               f"   Час: {schedule[num_of_class]['starts']} - {schedule[num_of_class]['ends']}🕑\n" \
               f"   Місце проведення: <em>{schedule[num_of_class]['classroom']}</em>📍\n" \
               f"   Викладач: {schedule[num_of_class]['lecturer']}👨‍🏫\n"


def construct_current_schedule(current):
    schedule = {}
    res = ""
    day = current[6]
    num_of_class = current[0]
    if day not in schedule:
        schedule[day] = {}
    if day not in res:
        res += f"<b>\n\n{day}\n</b>"
    schedule[day][num_of_class] = {}
    schedule[day][num_of_class]["starts"] = f"{current[1] if current[1] > 9 else f'0{current[1]}'}" \
                                            f":{current[2] if current[2] > 9 else f'0{current[2]}'}"
    schedule[day][num_of_class]["ends"] = f"{current[3] if current[3] > 9 else f'0{current[3]}'}" \
                                          f":{current[4] if current[4] > 9 else f'0{current[4]}'}"
    schedule[day][num_of_class]["classroom"] = current[5]
    schedule[day][num_of_class]["type"] = current[7]
    schedule[day][num_of_class]["subject"] = current[8]
    schedule[day][num_of_class]["lecturer"] = f"{current[9]} {current[10]} {current[11]}"

    res += structurize(schedule[day], num_of_class)
    return res


def construct_day_week_schedule(result):
    schedule = {}
    res = ""
    if result in ("Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"):
        return f"<b>\n\n{result}\n</b>" \
               f"Немає занять🥰\n"
    for line in result:
        day = line[7]
        num_of_class = line[1]
        if day not in schedule:
            schedule[day] = {}
        if len(schedule) == 1:
            if day not in res:
                res += f"<b>\n\n{day}\n</b>"
        for i in range(2, 6):
            if i == num_of_class:
                if i - 4 > 0:
                    if i - 4 not in schedule[day]:
                        ############## added
                        schedule[day][i-4] = "---"
                        ############## added
                        if len(schedule) == 1:
                            res += f"{i - 4}. ---\n"
                if i - 3 > 0:
                    if i - 3 not in schedule[day]:
                        ############## added
                        schedule[day][i-3] = "---"
                        ############## added
                        if len(schedule) == 1:
                            res += f"{i - 3}. ---\n"
                if i - 2 > 0:
                    if i - 2 not in schedule[day]:
                        ############## added
                        schedule[day][i-2] = "---"
                        ############## added
                        if len(schedule) == 1:
                            res += f"{i - 2}. ---\n"
                if i - 1 not in schedule[day]:
                    ############## added
                    schedule[day][i-1] = "---"
                    ############## added
                    if len(schedule) == 1:
                        res += f"{i - 1}. ---\n"
        schedule[day][num_of_class] = {}
        schedule[day][num_of_class]["starts"] = f"{line[2] if line[2] > 9 else f'0{line[2]}'}" \
                                                f":{line[3] if line[3] > 9 else f'0{line[3]}'}"
        schedule[day][num_of_class]["ends"] = f"{line[4] if line[4] > 9 else f'0{line[4]}'}" \
                                              f":{line[5] if line[5] > 9 else f'0{line[5]}'}"
        schedule[day][num_of_class]["classroom"] = line[6]
        schedule[day][num_of_class]["type"] = line[8]
        schedule[day][num_of_class]["subject"] = line[9]
        schedule[day][num_of_class]["lecturer"] = f"{line[10]} {line[11]} {line[12]}"
        if len(schedule) == 1:
            res += structurize(schedule[day], num_of_class)
    if len(schedule) == 1:
        return res
    res = ""
    days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"]
    for day in days:
        if day not in res:
            res += f"<b>\n\n{day}\n</b>"
        if day in schedule:
            for num_of_class in schedule[day]:
            # for num_class in range(1, len(schedule[day])+1):
            #     if num_of_class in schedule[day]:
                print(schedule[day], num_of_class)
                res += structurize(schedule[day], num_of_class)
        else:
            res += "Немає занять🥰\n"
    return res


def get_timestr(seconds):
    hours, remains = divmod(seconds, 3600)
    minutes, seconds = divmod(remains, 60)
    if hours >= 1:
        return f"{hours}год. {minutes}хв."
    return f"{minutes}хв."


# def structurize_sub_lec(combinations):
#     res = []
#     i = 0
#     for comb in combinations:
#         res.append(f"{comb[0]}. <b>{comb[2]}</b>({comb[1]})\n"
#                    f" - <em>{comb[4]} {comb[3]} {comb[5]}</em>\n")
#     return res

