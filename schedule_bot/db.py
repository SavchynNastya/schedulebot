from datetime import datetime

import mysql.connector

from structurize import construct_day_week_schedule, construct_current_schedule, get_timestr


class ScheduleDB:
    def __init__(self):
        """ Connect to the database """
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="fantastik4321",
            database="schedule"
        )
        self.cursor = self.connection.cursor()

    def get_groups(self):
        """ Get all the existing groups in database """
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT id_group FROM student_groups ")
            result = [item[0] for item in self.cursor.fetchall()]
            print("Groups: ", result)
            return result

    def get_week_schedule(self, group, week):
        """
        Get schedule of group in database
        Parameters
        ----------
        group : string
            Name of the group
        week : string
            "Парний" or "Непарний" week
        Returns
        ----------
        #?
        """
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT c.id_class, c.class_num, ci.start_hours, ci.start_minutes, "
                                "ci.end_hours, ci.end_minutes,classroom, day, sl.type_of_class, "
                                "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                "c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s "
                                "AND c.subj_info = sl.id_sub_lec AND sl.id_sub = s.id_subject "
                                "AND sl.id_lec = l.id_lecturer ",
                                (group, week))
            result = self.cursor.fetchall()
            # result = list(result)
            #
            # days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"]
            # for day in days:
            #     if day not in result:
            #         result.append(day)
            res = construct_day_week_schedule(result)
            return res

    def get_day_schedule(self, group, week, day):
        """
        """
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        if day > len(days)-1:
            day = day - len(days)
            week = "Непарний" if week == "Парний" else "Парний"
        day = days[day]

        res = ""
        if day == "Неділя":
            res = "Занять немає, відпочивай!"
        else:
            with self.connection:
                self.connection.reconnect()
                self.cursor.execute("SELECT c.id_class, c.class_num, ci.start_hours, ci.start_minutes, "
                                    "ci.end_hours, ci.end_minutes,classroom, day, sl.type_of_class, "
                                    "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                    "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                    "c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s "
                                    "AND c.day=%s AND c.subj_info = sl.id_sub_lec AND sl.id_sub = s.id_subject "
                                    "AND sl.id_lec = l.id_lecturer ORDER BY c.class_num ASC ",
                                    (group, week, day))
                result = self.cursor.fetchall()
                print(group, week, day)
                print(result)
                ids = {}
                for r in result:
                    ids[r[1]] = r[0]
                if len(result) == 0:
                    res = construct_day_week_schedule(day)
                else:
                    res = construct_day_week_schedule(result)
                    print(ids)
                    return ids, res
        return False, res

    def set_timing(self):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT ci.id_class, ci.start_hours, ci.start_minutes, "
                                "ci.end_hours, ci.end_minutes FROM class_info ci ")
            times = self.cursor.fetchall()

            class_info = {}
            for c in times:
                if c[0] not in class_info:
                    class_info[c[0]] = []
                start_time_str = "%(hours)s:%(minutes)s" % {
                    "hours": c[1],
                    "minutes": c[2]
                }
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time_str = "%(hours)s:%(minutes)s" % {
                    "hours": c[3],
                    "minutes": c[4]
                }
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                class_info[c[0]].append(start_time)
                class_info[c[0]].append(end_time)

        return class_info

    def get_current(self, group, week, day, hour, minutes):
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        day = days[day]

        if day == "Неділя":
            return "Сьогодні неділя, відпочивай, занять немає\n"

        current_time_str = "%(hours)s:%(minutes)s" % {
            "hours": hour,
            "minutes": minutes
        }
        current_time = datetime.strptime(current_time_str, "%H:%M").time()
        class_info = self.set_timing()

        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT class_num, ci.id_class FROM classes c, class_info ci "
                                "WHERE c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s AND c.day=%s",
                                (group, week, day))
            quantity = len(self.cursor.fetchall())

            print(class_info)
            res = ""
            current_class = ""
            for i in range(1, quantity+1):
                # print(class_info[i][0], current_time, class_info[i][1])
                if class_info[i][0] <= current_time <= class_info[i][1]:
                    current_class = i
                    left = get_timestr((datetime.combine(datetime.today(), class_info[i][1]) \
                           - datetime.combine(datetime.today(), current_time)).seconds)
                    res = f"До кінця пари {left}"
                elif i != quantity:
                    if class_info[i][1] <= current_time <= class_info[i+1][0]:
                        res = f"Зараз немає заняття, наступне через " \
                              f"{get_timestr((datetime.combine(datetime.today(), class_info[i+1][0]) - datetime.combine(datetime.today(), current_time)).seconds)}"
                        current_class += 1
            if res == "":
                return f"На сьогодні більше немає занять"
            # with self.connection:
            self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                "c.class_num = ci.id_class AND ci.id_class=%s  AND c.group_id=%s "
                                "AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                (current_class, group, week, day))
            current_class = self.cursor.fetchone()
            res += construct_current_schedule(current_class)
            return res

    def get_next(self, group, week, day, hour, minutes):
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

        current_time_str = "%(hours)s:%(minutes)s" % {
            "hours": hour,
            "minutes": minutes
        }
        current_time = datetime.strptime(current_time_str, "%H:%M").time()
        class_info = self.set_timing()

        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT class_num, ci.id_class FROM classes c, class_info ci "
                                "WHERE c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s AND c.day=%s",
                                (group, week, day))
            # classes = self.cursor.fetchall()
            # class_nums = [c[0] for c in classes]
            # print(classes)
            # print(class_nums)
            quantity = len(self.cursor.fetchall())

        print(class_info)
        res = ""
        cur_day = days[day]

        current_class, next_class = 0, 0
        for i in range(1, quantity+1):
            if class_info[i][0] <= current_time <= class_info[i][1] or class_info[i][1] < current_time < class_info[i+1][0]:
                current_class = i
        if current_class != 0:
            next_class = current_class + 1

        if not next_class:
            res = f"Наступного заняття у групі {group} сьогодні немає.\n"
            if cur_day == "П'ятниця":
                with self.connection:
                    self.connection.reconnect()
                    self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                        "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                        "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                        "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                        "c.class_num = ci.id_class AND c.group_id=%s "
                                        "AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                        "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                        (group, week, "Субота"))
                    next_class = self.cursor.fetchone()
                    if next_class:
                        res += f"Наступне заняття: {construct_current_schedule(next_class)}"
                        return res
                    else:
                        cur_day = "Субота"
            if cur_day == "Субота" or cur_day == "Неділя":
                with self.connection:
                    self.connection.reconnect()
                    self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                        "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                        "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                        "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                        "c.class_num = ci.id_class AND c.group_id=%s "
                                        "AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                        "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                        (group, "Непарний" if week == "Парний" else "Парний", "Понеділок"))
                    next_class = self.cursor.fetchone()
                    res += f"Наступне заняття: {construct_current_schedule(next_class)}"
                    return res
            else:
                while True:
                    day += 1
                    if day >= len(days) - 1:
                        day -= 1
                        day = day - len(days) - 1
                    next_day = days[day]
                    with self.connection:
                        self.connection.reconnect()
                        self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                            "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                            "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                            "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                            "c.class_num = ci.id_class  AND c.group_id=%s "
                                            "AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                            "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                            (group, week, next_day))
                        next_tomorrow = self.cursor.fetchone()
                        if next_tomorrow:
                            next_tomorrow = construct_current_schedule(next_tomorrow)
                            res += next_tomorrow
                            return res
        else:
            with self.connection:
                self.connection.reconnect()
                self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                    "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                    "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                    "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                    "c.class_num = ci.id_class AND ci.id_class=%s  AND c.group_id=%s "
                                    "AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                    "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                    (next_class, group, week, cur_day))
                next_class = self.cursor.fetchone()
                res += construct_current_schedule(next_class)
            return res

    def get_time(self, group, week, day, hour, minutes):
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

        current_time_str = "%(hours)s:%(minutes)s" % {
            "hours": hour,
            "minutes": minutes
        }
        current_time = datetime.strptime(current_time_str, "%H:%M").time()
        day = days[day]

        class_info = self.set_timing()

        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT class_num, ci.id_class FROM classes c, class_info ci "
                                "WHERE c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s AND c.day=%s",
                                (group, week, day))
            quantity = len(self.cursor.fetchall())

            if quantity:
                res = ""
                current_class, next_class = 0, 0
                for i in range(1, quantity + 1):
                    if class_info[i][0] <= current_time < class_info[i][1]:
                        res = f"До кінця заняття: " \
                              f"{get_timestr((datetime.combine(datetime.today(), class_info[i][1]) - datetime.combine(datetime.today(), current_time)).seconds)}"
                    elif class_info[i][1] < current_time < class_info[i+1][0]:
                        res = f"Наступне заняття через: " \
                              f"{get_timestr((datetime.combine(datetime.today(), class_info[i+1][0]) - datetime.combine(datetime.today(), current_time)).seconds)}"
                    else:
                        res = f"Заняття немає, відпочивай!\n"
            else:
                res = f"Заняття немає, відпочивай!\n"
            return res

    def get_coincidence_classroom(self):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT * FROM classes")
            all_classes = self.cursor.fetchall()

            res = ""
            time_classroom = []
            for cl in all_classes:
                # print(cl)
                if (cl[1], cl[3], cl[5], cl[6]) not in time_classroom:
                    time_classroom.append((cl[1], cl[3], cl[5], cl[6]))
                else:
                    data = [cl[0], cl[2], cl[5], cl[6], cl[1], cl[3]]
                    res = f"Група {cl[2]}, {cl[5]}, {cl[6]} тижнень, заняття №{cl[1]} потребує перевибору аудиторії.\n" \
                          f"{cl[3]} вже зайнято.\n"
            time_classroom.clear()
            if res == "":
                return "", res
            return data, res

    def get_coincidence_lecturer(self):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT id_class, class_num, group_id, classroom, day, week, "
                                "l.name, l.surname, l.patronymic, s.name, sl.id_sub_lec FROM classes c "
                                "INNER JOIN subject_lecturer sl ON c.subj_info = sl.id_sub_lec "
                                "INNER JOIN lecturers l ON sl.id_lec = l.id_lecturer "
                                "INNER JOIN subject s ON sl.id_sub = s.id_subject")
            lecturers_classnums = self.cursor.fetchall()
            res = ""
            lect_classnum_combination = []
            for lc in lecturers_classnums:
                # print(lc)
                if (lc[1], lc[4], lc[5], lc[6], lc[7], lc[8]) not in lect_classnum_combination:
                    lect_classnum_combination.append((lc[1], lc[4], lc[5], lc[6], lc[7], lc[8]))
                else:
                    data = [lc[0], lc[1], lc[2], lc[3], lc[4], lc[5], lc[6], lc[7], lc[8], lc[9], lc[10]]
                    print(data)
                    res = f"{lc[4]}, {lc[5]} тижнень, заняття №{lc[1]} - {lc[9]} у групі {lc[2]}" \
                          f"повинно бути замінено.\n" \
                          f"Викладач {lc[6]} {lc[7]} {lc[8]} зайнятий у цей час.\n"
            lect_classnum_combination.clear()
            if res == "":
                return "", res
            return data, res

    def check_new_classroom(self, new_classroom, day, class_num, type_of_week):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT * FROM classes c WHERE classroom=%s AND "
                                "class_num=%s AND day=%s AND week=%s",
                                (new_classroom, class_num, day, type_of_week))
            classes = self.cursor.fetchall()
            if classes:
                # return f"{new_classroom} зайнятий у цей час!\n"
                return True
            else:
                return False

    def change_classroom(self, id, new_classroom):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("UPDATE classes SET classroom=%s WHERE id_class=%s",
                                (new_classroom, id))
            self.connection.commit()
            return True

    def get_lecturers(self, class_num, subject, day, week, current_lec):
        with self.connection:
            self.connection.reconnect()
            # print(current_lec)
            self.cursor.execute('''SELECT l.id_lecturer, l.surname FROM lecturers l
                                INNER JOIN subject_lecturer sl ON sl.id_lec = l.id_lecturer
                                WHERE sl.id_sub_lec=%s''', (current_lec, ))
            id_lecturer = self.cursor.fetchone()[0]
            self.cursor.execute('''SELECT DISTINCT sl.id_sub_lec, sl.type_of_class, s.name, l.surname, 
                                l.name, l.patronymic FROM lecturers l 
                                INNER JOIN subject_lecturer sl ON l.id_lecturer = sl.id_lec
                                INNER JOIN subject s ON sl.id_sub = s.id_subject 
                                WHERE s.name=%s AND sl.id_lec!=%s AND sl.id_sub_lec NOT IN (
                                   SELECT c.subj_info FROM classes c WHERE c.class_num!=%s AND c.day=%s AND c.week=%s)''',
                                (subject, id_lecturer, class_num, day, week))
            combinations = self.cursor.fetchall()
            # print(combinations)
            if combinations:
                return combinations
                # return structurize_sub_lec(combinations)
            else:
                return ""


    def get_sub_lec(self, class_num, day, week):
        with self.connection:
            self.connection.reconnect()
            # self.cursor.execute('''SELECT DISTINCT sl.id_sub_lec, sl.type_of_class, s.name, l.surname,
            #                     l.name, l.patronymic FROM lecturers l
            #                     INNER JOIN subject_lecturer sl ON l.id_lecturer = sl.id_lec
            #                     INNER JOIN subject s ON sl.id_sub = s.id_subject
            #                     WHERE sl.id_sub_lec NOT IN (
            #                        SELECT c.subj_info FROM classes c WHERE c.class_num=%s AND
            #                     c.day=%s AND c.week=%s)''', (class_num, day, week))
            self.cursor.execute('''
                                SELECT DISTINCT sl.id_sub_lec, sl.type_of_class, s.name, l.surname,  
                                l.name, l.patronymic FROM lecturers l 
                                INNER JOIN subject_lecturer sl ON l.id_lecturer = sl.id_lec 
                                INNER JOIN subject s ON sl.id_sub = s.id_subject  
                                WHERE sl.id_lec NOT IN ( 
                                   SELECT sl.id_lec FROM subject_lecturer sl
                                   INNER JOIN classes c ON c.subj_info=sl.id_sub_lec
                                   WHERE c.class_num=%s AND c.day=%s AND c.week=%s)
                                ''', (class_num, day, week))
            combinations = self.cursor.fetchall()
            return combinations
            # return structurize_sub_lec(combinations)

    def set_lec_sub(self, id, lec_sub):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT class_num, day, week FROM classes WHERE id_class=%s",
                                (id, ))
            info = self.cursor.fetchone()

            self.cursor.execute("SELECT id_class FROM classes WHERE class_num=%s AND day=%s AND week=%s AND subj_info=%s",
                                (info[0], info[1], info[2], lec_sub))
            coincidence = self.cursor.fetchall()
            if coincidence:
                return False

            self.cursor.execute("UPDATE classes SET subj_info=%s WHERE id_class=%s",
                                (lec_sub, id))
            update = self.connection.commit()
            print(update)
            # return update
            return True


    def check_sub_lec_id(self, id):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT subject.name, lecturers.name, "
                                "lecturers.surname, lecturers.patronymic FROM subject_lecturer "
                                "INNER JOIN lecturers ON id_lec = lecturers.id_lecturer "
                                "INNER JOIN subject ON id_sub = subject.id_subject "
                                "WHERE id_sub_lec=%s", (id, ))
            check = self.cursor.fetchone()
            if check:
                return True
            return False

    def check_class_num(self, group, week, day, class_num):
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        day = days[int(day)]
        with self.connection:
            self.connection.reconnect()
            # self.cursor.execute("SELECT id_class FROM classes WHERE class_num=%s AND "
            #                     "group_id=%s AND day=%s AND week=%s",
            #                     (class_num, group, day, week))
            self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
                                "ci.end_hours, ci.end_minutes, classroom, day, sl.type_of_class, "
                                "s.name, l.surname, l.name, l.patronymic FROM classes c, "
                                "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
                                "c.class_num=%s AND c.group_id=%s AND c.week=%s AND "
                                "c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                (class_num, group, week, day))
            check = self.cursor.fetchone()
            if not check:
                return False
            else:
                check = construct_current_schedule(check)
                return check

    def change_by_id(self, group, week, day, class_num, classroom, sub_lec):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT id_class FROM classes c, class_info ci, subject_lecturer sl, "
                                "subject s, lecturers l WHERE c.class_num=%s AND ci.id_class=%s  "
                                "AND c.group_id=%s AND c.week=%s AND c.day=%s AND c.subj_info = sl.id_sub_lec AND "
                                "sl.id_sub = s.id_subject AND sl.id_lec = l.id_lecturer",
                                (class_num, group, week, day))
            id_class = self.cursor.fetchone()

            self.cursor.execute("UPDATE classes SET classroom=%s, subj_info=%s"
                                "WHERE id_class=%s",
                                (classroom, sub_lec, id_class))
            self.connection.commit()
            return True

    def add_class(self, group, week, day, class_num, classroom, sub_lec):
        days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        day = days[int(day)]
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("SELECT MAX(id_class) FROM classes")
            last_id = self.cursor.fetchone()[0]
            id = last_id + 1
            print(id, group, week, day, class_num, classroom, sub_lec)
            self.cursor.execute("INSERT INTO classes VALUES "
                                "(%s, %s, %s, %s, %s, %s, %s)",
                                (id, class_num, group, classroom, sub_lec, day, week))
            self.connection.commit()
            return True

    def delete_class(self, class_id):
        with self.connection:
            self.connection.reconnect()
            self.cursor.execute("DELETE FROM classes WHERE id_class=%s", (class_id, ))
            delete = self.connection.commit()
            return True


    # def get_tomorrow(self, group, week, day):
    #     days = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    #     tomorrow_day = days[day+1]
    #
    #     res = ""
    #
    #     if tomorrow_day == "Неділя":
    #         res = "Завтра неділя - немає занять:)\n"
    #     else:
    #         with self.connection:
    #             self.connection.reconnect()
    #             self.cursor.execute("SELECT class_num, ci.start_hours, ci.start_minutes, "
    #                                 "ci.end_hours, ci.end_minutes,classroom, day, sl.type_of_class, "
    #                                 "s.name, l.surname, l.name, l.patronymic FROM classes c, "
    #                                 "class_info ci,subject_lecturer sl, subject s, lecturers l WHERE "
    #                                 "c.class_num = ci.id_class AND c.group_id=%s AND c.week=%s "
    #                                 "AND c.day=%s AND c.subj_info = sl.id_sub_lec AND sl.id_sub = s.id_subject "
    #                                 "AND sl.id_lec = l.id_lecturer ORDER BY c.class_num ASC ",
    #                                 (group, week, tomorrow_day))
    #             result = self.cursor.fetchall()
    #             res = f"<b>Розклад на завтра</b>: {construct_day_week_schedule(result)}"
    #     return res

