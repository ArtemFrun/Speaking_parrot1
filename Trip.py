import telebot
import sqlite3
import customData
import time
from datetime import datetime
from telebot import types
from geopy.distance import geodesic

bot = telebot.TeleBot(customData.TOKEN)
conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()

###Создание поездки
def trip_pas(dispatch, expectation, price, lon_pas, lat_pas, chat_id, date_Create):
    global status_trip
    status_trip = 1
    now = datetime.now()
    day = datetime(now.year, now.month, now.day)
    rez = (now - day)
    now_sec = int(rez.total_seconds())
    info_trip = [dispatch, expectation, price, lon_pas, lat_pas, chat_id, status_trip, date_Create, now_sec]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',(info_trip))
    con.commit()
    return

###Отмена поездки пасажиром
def change_trip_pas(chat_id, status_trip):
    with sqlite3.connect("mydb.sqlite") as con:
        chat_id_pas = chat_id
        status_trip_pas = status_trip
        cur = con.cursor()
    cur.execute('UPDATE trip SET status_trip=? WHERE chat_id=?', (status_trip_pas, chat_id_pas))
    con.commit()
    return


def START_SEARCH_PAS(message):
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
    btn_start = types.KeyboardButton('Поиск пассажира')
    markup_menu.add(btn_start)
    bot.send_message(message.chat.id, "Для начала поиска нажмите \"Поиск пассажира\"", reply_markup=markup_menu)
    return

###Отображение активных заказов
def active_search_passenger(message, num, count, lon_dr, lat_dr):
    global keyboards
    global trip_num
    global order1
    global order2
    global order3
    global order4
    global order5
    global counter
    order1 = 0
    order2 = 0
    order3 = 0
    order4 = 0
    order5 = 0
    counter = count
    trip_num = num
    keyboards = []
    bot.send_message(message.chat.id, "Начало поиска")
    now = datetime.now()
    day = datetime(now.year, now.month, now.day)
    rez = (now - day)
    now_sec = int(rez.total_seconds())
    data_Create_dr = time.strftime("%Y.%m.%d", time.localtime())
    time_Create_dr = now_sec - 600
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    with con:
        cur.execute('SELECT * FROM trip WHERE data_seconds<? AND date_Create=? AND status_trip=1',
                    (time_Create_dr, data_Create_dr))
        rows = cur.fetchall()
        while True:

            try:
                row = rows[trip_num]
            except IndexError:
                markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                btn_restart = types.KeyboardButton('Поиск пассажира')
                markup_menu.add(btn_restart)
                bot.send_message(message.chat.id, "Больше нету заказов. Для начала поиска нажмите \"Поиск пассажира\"",
                                 reply_markup=markup_menu)
                trip_num = 0
                return order1, order2, order3, order4, order5

            result = float('{:.2f}'.format(geodesic((row[3], row[4]), (lon_dr, lat_dr)).km))

            if trip_num == 0 + counter:
                order1 = trip_num
                keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='trip1')
                keyboard.add(key_yes)
            elif trip_num == 1 + counter:
                order2 = trip_num
                keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='trip2')
                keyboard.add(key_yes)
            elif trip_num == 2 + counter:
                order3 = trip_num
                keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='trip3')
                keyboard.add(key_yes)
            elif trip_num == 3 + counter:
                order4 = trip_num
                keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='trip4')
                keyboard.add(key_yes)
            elif trip_num == 4 + counter:
                order5 = trip_num
                keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='trip5')
                keyboard.add(key_yes)

            trip = ('Откуда: ' + row[0] + '\nКуда: ' + row[1] + '\nЦена: ' + str(row[2]) + '\nРастояние: ' + str(
                result)
                    + ' КМ')
            bot.send_message(message.chat.id, trip, reply_markup=keyboard)

            if (trip_num + 1) % 5 == 0:
                markup_trip = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                        row_width=1)  ###Продолжение поиска поездки
                btn_search = types.KeyboardButton('Продолжить поиск')
                markup_trip.add(btn_search)
                bot.send_message(message.chat.id, "Для просмотра следущих заказов, нажмите \"Продолжить поиск\"",
                                 reply_markup=markup_trip)
                return order1, order2, order3, order4, order5

            trip_num = trip_num + 1

###продолжить поиск
def continue_search(message):
    count = counter + 5
    num = trip_num + 1
    return count, num



###Сообщение пассажиру о прийоме его заказа
def message_for_passenger(message, time_arrival, chat_id_passenger, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?',(chat_id_dr))
        while True:
            row = cur.fetchone()



            if (row[8] == 0):
                star = 0
            else:
                star = "{0:.2f}".format(int(row[9]) / int(row[8]))

            info_dr = ('Ваш заказ принят, машина будет через ' + str(time_arrival) + ' мин.\n\n' + 'Автомобиль марки: ' + row[7]
                       + '\nНомерной знак: ' + row[6] + '\nЦвет: ' + row[5] + '\n\nРейтинг водителя: ' + str(star)+ ' ⭐️')
            bot.send_message(chat_id_passenger, info_dr)
            return



###Сообщение о прибытие автомобиля
def car_in_place(message, chat_id_passenger, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?', (chat_id_dr))
        while True:
            row = cur.fetchone()

            if (row[8] == 0):
                star = 0
            else:
                star = "{0:.2f}".format(int(row[9]) / int(row[8]))

            info_dr = ('Автомобиль на месте. Можите выходить.\n\n' + 'Автомобиль марки: ' + row[7]
                       + '\nНомерной знак: ' + row[6] + '\nЦвет: ' + row[5] + '\n\nРейтинг водителя: ' + str(star) + ' ⭐️')
            bot.send_message(chat_id_passenger, info_dr)

            return



###Оценка за поездку
def review_drive(message, chat_id_passenger):
    keyboard = types.InlineKeyboardMarkup()
    key_star = types.InlineKeyboardButton(text='5 ⭐️', callback_data='5_star')
    keyboard.add(key_star)
    key_star = types.InlineKeyboardButton(text='4 ⭐️', callback_data='4_star')
    keyboard.add(key_star)
    key_star = types.InlineKeyboardButton(text='3 ⭐️', callback_data='3_star')
    keyboard.add(key_star)
    key_star = types.InlineKeyboardButton(text='2 ⭐️', callback_data='2_star')
    keyboard.add(key_star)
    key_star = types.InlineKeyboardButton(text='1 ⭐️', callback_data='1_star')
    keyboard.add(key_star)
    bot.send_message(chat_id_passenger, 'Поставте оценку за поездку.', reply_markup=keyboard)
    return


###Запись оценки в рейтинг водителя
def review_rating_drive(message, star, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?', (chat_id_dr))
        row = cur.fetchone()

        reting_dr = int(row[9]) + star
        num_reting = int(row[8]) + 1

        cur.execute('UPDATE drive SET number_of_ratings=?, sum_of_ratings = ? WHERE chat_id=?', (num_reting, reting_dr, chat_id_drive))

        return



### Начать поездку (переход на создания поездки)
def START_TRIP(message):
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
    btn_location = types.KeyboardButton('Начать поездку')
    markup_menu.add(btn_location)
    bot.send_message(message.chat.id, "Для поиска автомобиля нажмите на кнопкую. Начать поездку",
                         reply_markup=markup_menu)
    return

