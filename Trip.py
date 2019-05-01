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


###Отображение активных заказов
def active_search_passenger(message, lon_dr,  lat_dr, i):
    now = datetime.now()
    day = datetime(now.year, now.month, now.day)
    rez = (now - day)
    now_sec = int(rez.total_seconds())
    data_Create_dr = time.strftime("%Y.%m.%d", time.localtime())
    time_Create_dr = now_sec - 600
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    with con:
        cur.execute('SELECT * FROM trip WHERE data_seconds<? AND date_Create=? AND status_trip=1', (time_Create_dr, data_Create_dr))
        while True:
            row = cur.fetchone()

            if row == None:
                markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                btn_search = types.KeyboardButton('Поиск пассажира')
                markup_menu.add(btn_search)
                bot.send_message(message.chat.id, "Больше нету заказов. Для начала поиска нажмите \"Поиск пассажира\"",
                                 reply_markup=markup_menu)
                return

            result = float('{:.2f}'.format(geodesic((row[3], row[4]), (lon_dr,  lat_dr)).km))

            keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
            key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data='Accept')
            keyboard.add(key_yes)

            trip = ('Откуда: ' + row[0] + '\nКуда: ' + row[1] + '\nЦена: ' + str(row[2]) + '\nРастояние: ' + str(result)
                    + ' КМ')
            bot.send_message(message.chat.id, trip, reply_markup=keyboard)


            if (i+1)%5 == 0:
                markup_trip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###Продолжение поиска поездки
                btn_search = types.KeyboardButton('Продолжить поиск')
                markup_trip.add(btn_search)
                bot.send_message(message.chat.id, "Для просмотра следущих заказов, нажмите \"Продолжить поиск\"",
                                 reply_markup=markup_trip)
                break

            i = i + 1

    if message.text == "Продолжить поиск":
        active_search_passenger(message, lon_dr,  lat_dr, i)



def message_for_passenger(message, time_arrival, chat_id_passenger, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?',(chat_id_dr))
        while True:
            row = cur.fetchone()

            info_dr = ('Ваш заказ принят, машина будет через ' + str(time_arrival) + ' мин.\n\n' + 'Автомобиль марки: ' + row[7]
                       + '\nНомерной знак: ' + row[6] + '\nЦвет: ' + row[5] + '\n\nРейтинг водителя: ' + str(int(row[9])/int(row[8]))+ ' ⭐️')
            bot.send_message(chat_id_passenger, info_dr)
            return


def car_in_place(message, chat_id_passenger, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?', (chat_id_dr))
        while True:
            row = cur.fetchone()

            info_dr = ('Автомобиль на месте. Можите выходить.\n\n' + 'Автомобиль марки: ' + row[7]
                       + '\nНомерной знак: ' + row[6] + '\nЦвет: ' + row[5] + '\n\nРейтинг водителя: ' + str(int(row[9])/int(row[8])) + ' ⭐️')
            bot.send_message(chat_id_passenger, info_dr)

            return


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

def review_rating_drive(message, star, chat_id_drive):
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    chat_id_dr = [chat_id_drive]
    with con:
        cur.execute('SELECT * FROM drive WHERE chat_id=?', (chat_id_dr))
        while True:
            row = cur.fetchone()

            reting_dr = int(row[9]) + star
            num_reting = int(row[8]) + 1

            cur.execute('UPDATE drive SET number_of_ratings=? AND sum_of_ratings = ? WHERE chat_id=?', (num_reting, reting_dr, chat_id_drive))
            con.commit()

            return
