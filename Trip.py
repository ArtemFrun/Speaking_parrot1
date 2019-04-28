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
    date_Create = time.strftime("%Y.%m.%d", time.localtime())
    info_trip = [dispatch, expectation, price, lon_pas, lat_pas, chat_id, status_trip, date_Create, now_sec]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',(info_trip))
    con.commit()
    return

###Отмена поездки пасажиром
def cancel_trip_pas(chat_id):
    with sqlite3.connect("mydb.sqlite") as con:
        chat_id_pas = [chat_id]
        cur = con.cursor()
    cur.execute('UPDATE trip SET status_trip=4 WHERE chat_id=?', (chat_id_pas))
    con.commit()
    return


###Отображение активных заказов
def active_search_passenger(message, lon_dr,  lat_dr):
    now = datetime.now()
    day = datetime(now.year, now.month, now.day)
    rez = (now - day)
    now_sec = int(rez.total_seconds())
    data_Create_dr = time.strftime("%Y.%m.%d", time.localtime())
    time_Create_dr = now_sec - 600
    con = sqlite3.connect("mydb.sqlite")
    cur = con.cursor()
    with con:
        cur.execute('SELECT * FROM trip WHERE data_seconds>? AND date_Create=? AND status_trip=1', (time_Create_dr,data_Create_dr))
        i=0
        while True:
            row = cur.fetchone()

            if row == None:
                markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                btn_search = types.KeyboardButton('Поиск пассажира')
                markup_menu.add(btn_search)
                bot.send_message(message.chat.id, "Больше нету заказов. Для начала поиска нажмите \"Поиск пассажира\"",
                                 reply_markup=markup_menu)
                return

            result = float('{:.2f}'.format(geodesic((row[3],row[4]), (lon_dr,  lat_dr)).km))

            trip = ('Откуда: ' + row[0] + '\nКуда: ' + row[1] + '\nЦена: ' + str(row[2]) + '\nРастояние: ' + str(result) + ' КМ')
            bot.send_message(message.chat.id, trip)


            if i+1%5 == 0:
                markup_trip = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                btn_search = types.KeyboardButton('Продолжить поиск')
                markup_trip.add(btn_search)
                bot.send_message(message.chat.id, "Для просмотра следущих заказов, нажмите \"Продолжить поиск\"",
                                 reply_markup=markup_trip)
                if message.text == "Продолжить поиск":
                    break

            i = i + 1
