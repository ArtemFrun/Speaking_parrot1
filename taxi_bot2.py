#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3
import customData
import Trip
import Reg
import time
from datetime import timedelta, datetime
from geopy.distance import geodesic

conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()

###, request_location=True
bot = telebot.TeleBot(customData.TOKEN)

###Таблиця с данными пассажиров
try:
    cursor.execute(
        '''CREATE TABLE passenger (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER)''')
except:
    pass
###Таблица поездок. Обозначения статуса: 1 - активный поиск поездки, 2 - заказ в работе, 3 - заказ выполнен, 4 - заказ отменен.
try:
    cursor.execute(
        '''CREATE TABLE trip (dispatch TEXT, expectation TEXT, price INTEGER, lon_pas FLOAT, lat_pas FLOAT, 
            chat_id INTEGER, status_trip INTEGER, date_Create TEXT, data_seconds INTEGER)''')
except:
    pass
###Таблица регистрации водителей.
try:
    cursor.execute(
        '''CREATE TABLE drive (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER, 
            color_car TEXT, number_car TEXT, car_model TEXT, number_of_ratings INTEGER, sum_of_ratings INTEGER)''')
except:
    pass


###Начало бота и выбор регистрации.
@bot.message_handler(commands=['start'])
def send_welcom(message):
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Для пасажира', callback_data='pas')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='Для водителяя', callback_data='dr')
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, 'Привет! Я бот такси. Пройди регистрацию.', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "pas")
def passenger(call):
    global type
    type = 'passenger'
    bot.send_message(call.message.chat.id, "Номер телефона")
    bot.register_next_step_handler(call.message, get_phone)


@bot.callback_query_handler(func=lambda call: call.data == "dr")
def drive(call):
    global type
    type = 'drive'
    bot.send_message(call.message.chat.id, "Номер телефона")
    bot.register_next_step_handler(call.message, get_phone_dr)


@bot.callback_query_handler(func=lambda call: call.data == "YES_pas_reg")
def reg_pas(call):
    Reg.get_reg(call.message)
    ###bot.register_next_step_handler(call.message, get_reg(call.message))


@bot.callback_query_handler(func=lambda call: call.data == "NO_pas_reg")
def no_reg_pas(call):
    bot.send_message(call.message.chat.id, "Номер телефона")
    bot.register_next_step_handler(call.message, get_phone)


@bot.callback_query_handler(func=lambda call: call.data == "YES_pas_dr")
def reg_dr(call):
    Reg.get_reg_dr(call.message)
    ###bot.register_next_step_handler(call.message, get_reg_dr(call.message))


@bot.callback_query_handler(func=lambda call: call.data == "NO_pas_dr")
def no_reg_dr(call):
    bot.send_message(call.message.chat.id, "Номер телефона")
    bot.register_next_step_handler(call.message, get_phone_dr)


@bot.callback_query_handler(func=lambda call: call.data == "trip1")
def trip1(call):
    bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
    accept_trip_drive(call.message, order1)


@bot.callback_query_handler(func=lambda call: call.data == "trip2")
def trip2(call):
    bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
    accept_trip_drive(call.message, order2)


@bot.callback_query_handler(func=lambda call: call.data == "trip3")
def trip3(call):
    bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
    accept_trip_drive(call.message, order3)


@bot.callback_query_handler(func=lambda call: call.data == "trip4")
def trip4(call):
    bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
    accept_trip_drive(call.message, order4)


@bot.callback_query_handler(func=lambda call: call.data == "trip5")
def trip5(call):
    bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
    accept_trip_drive(call.message, order5)


@bot.callback_query_handler(func=lambda call: call.data == "YES_trip_dr")
def YES_TRIP_DR(call):
    Trip.change_trip_pas(chat_id_passenger, 2)
    time_arrival_drive(call.message)  # Запрос на время прибытия


@bot.callback_query_handler(func=lambda call: call.data == "NO_trip_dr")
def NO_TRIP_DR(call):
    Trip.START_SEARCH_PAS(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "1_time")
def time1(call):
    global time_arrival
    time_arrival = 1
    Trip.message_for_passenger(call.message, time_arrival, chat_id_passenger, chat_id_drive)
    accepted_teip_drive(call.message, time_arrival)


@bot.callback_query_handler(func=lambda call: call.data == "3_time")
def time3(call):
    global time_arrival
    time_arrival = 3
    Trip.message_for_passenger(call.message, time_arrival, chat_id_passenger, chat_id_drive)
    accepted_teip_drive(call.message, time_arrival)


@bot.callback_query_handler(func=lambda call: call.data == "5_time")
def time5(call):
    global time_arrival
    time_arrival = 5
    Trip.message_for_passenger(call.message, time_arrival, chat_id_passenger, chat_id_drive)
    accepted_teip_drive(call.message, time_arrival)


@bot.callback_query_handler(func=lambda call: call.data == "10_time")
def time10(call):
    global time_arrival
    time_arrival = 10
    Trip.message_for_passenger(call.message, time_arrival, chat_id_passenger, chat_id_drive)
    accepted_teip_drive(call.message, time_arrival)


@bot.callback_query_handler(func=lambda call: call.data == "arrived")
def arrived(call):
    Trip.car_in_place(call.message, chat_id_passenger, chat_id_drive)
    accepted_teip_drive(call.message, time_arrival)


@bot.callback_query_handler(func=lambda call: call.data == "to_cancel")
def to_cancel(call):
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
    btn_start = types.KeyboardButton('Поиск пассажира')
    markup_menu.add(btn_start)
    bot.send_message(call.message.chat.id, "Для начала поиска нажмите \"Поиск пассажира\"", reply_markup=markup_menu)


@bot.callback_query_handler(func=lambda call: call.data == "fulfilled")
def fulfilled(call):
    Trip.review_drive(call.message, chat_id_passenger)
    Trip.START_SEARCH_PAS(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "5_star")
def star_5(call):
    star = 5
    Trip.review_rating_drive(call.message, star, chat_id_drive)
    bot.edit_message_text('Оценка оставлена', call.message.chat.id, call.message.message_id)
    Trip.START_TRIP(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "4_star")
def star_4(call):
    star = 4
    Trip.review_rating_drive(call.message, star, chat_id_drive)
    bot.edit_message_text('Оценка оставлена', call.message.chat.id, call.message.message_id)
    Trip.START_TRIP(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "3_star")
def star_3(call):
    star = 3
    Trip.review_rating_drive(call.message, star, chat_id_drive)
    bot.edit_message_text('Оценка оставлена', call.message.chat.id, call.message.message_id)
    Trip.START_TRIP(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "2_star")
def star_2(call):
    star = 2
    Trip.review_rating_drive(call.message, star, chat_id_drive)
    bot.edit_message_text('Оценка оставлена', call.message.chat.id, call.message.message_id)
    Trip.START_TRIP(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "1_star")
def star_1(call):
    star = 1
    Trip.review_rating_drive(call.message, star, chat_id_drive)
    bot.edit_message_text('Оценка оставлена', call.message.chat.id, call.message.message_id)
    Trip.START_TRIP(call.message)


###Регистрация пасажира
###Прийом номера телефона
def get_phone(message):
    Reg.get_phone(message)
    bot.register_next_step_handler(message, get_name)


###Прийом Имени
def get_name(message):
    Reg.get_name(message)
    bot.register_next_step_handler(message, get_surname)


###Прийом Фамилии
def get_surname(message):
    Reg.get_surname(message)


###Запись данных в БД.
'''
def get_reg(message):
    Reg.get_reg(message)
'''

###Конец регистрации пасажира


###Регистрация водителя
def get_phone_dr(message):
    Reg.get_phone(message)
    bot.register_next_step_handler(message, get_name_dr)


def get_name_dr(message):
    Reg.get_name(message)
    bot.register_next_step_handler(message, get_surname_dr)


def get_surname_dr(message):
    Reg.get_surname_dr(message)
    bot.register_next_step_handler(message, get_color_car)


def get_color_car(message):
    Reg.get_color_car(message)
    bot.register_next_step_handler(message, get_number_car)


def get_number_car(message):
    Reg.get_number_car(message)
    bot.register_next_step_handler(message, get_car_model)


def get_car_model(message):
    Reg.get_car_model(message)

'''
def get_reg_dr(message):
    Reg.get_reg_dr(message)
'''

###Конец регистрации водителя


### Начало поездки

@bot.message_handler(func=lambda message: message.text == "Начать поездку")
def trip(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Поиск пассажира")
def trip_dr(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                     reply_markup=keyboard)


###Передача геоданых
@bot.message_handler(func=lambda message: True, content_types=['location'])
def location_pas(message):
    type = 'drive'
    if type == 'passenger':
        global lon_pas
        global lat_pas
        lon_pas = message.location.longitude
        lat_pas = message.location.latitude
        bot.send_message(message.chat.id, "Введите адрес от куда будем ехать. Улица, дом, падезд.")
        bot.register_next_step_handler(message, arrivel)
    elif type == 'drive':
        global lon_dr
        global lat_dr
        lon_dr = message.location.longitude
        lat_dr = message.location.latitude
        location_drive(message, 0, 0)


### Для пассажира (адрес прибытия)
def arrivel(message):
    global dispatch
    dispatch = message.text
    bot.send_message(message.chat.id, "Введите адрес куда едим. Улица, дом.")
    bot.register_next_step_handler(message, expectation)

###Прийом адресса приьытия запрос на стоимость поездки
def expectation(message):
    global expectation
    expectation = message.text
    bot.send_message(message.chat.id, "Введите суму")
    bot.register_next_step_handler(message, trip_price)

###Запись поездки в БД
def trip_price(message):
    global price
    global chat_id
    date_Create = time.strftime("%Y.%m.%d", time.localtime())
    chat_id = message.chat.id
    price = int(message.text)
    bot.send_message(message.chat.id, "Поиск машины")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отменить")
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Для отмены нажмите кнопку... Отменить ", reply_markup=keyboard)
    Trip.trip_pas(dispatch, expectation, price, lon_pas, lat_pas, chat_id, date_Create)
    bot.register_next_step_handler(message, cancel_trip)

###Отмена поездки
def cancel_trip(message):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Для подтвержения отмены, наберите. Да")
        bot.register_next_step_handler(message, conf_cancel_trip)

###Подтверждения отмены поездки
def conf_cancel_trip(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Поиск отменен")
        status_trip_pas = 4
        Trip.change_trip_pas(chat_id, status_trip_pas)
        Trip.START_TRIP(message)
    else:
        bot.send_message(message.chat.id, "Введено не верно. Повторите попитку")
        bot.register_next_step_handler(message, conf_cancel_trip)


###Конец поездки пассажира


### Начало поиска пассажира
def location_drive(message, num, count):
    global order1
    global order2
    global order3
    global order4
    global order5
    order1, order2, order3, order4, order5 = Trip.active_search_passenger(message, num, count, lon_dr, lat_dr)

'''
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
        cur.execute('SELECT * FROM trip WHERE data_seconds>? AND date_Create=? AND status_trip=1',
                    (time_Create_dr, data_Create_dr))
        while True:
            row = cur.fetchone()

            if row == None:
                markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                btn_restart = types.KeyboardButton('Поиск пассажира')
                markup_menu.add(btn_restart)
                bot.send_message(message.chat.id, "Больше нету заказов. Для начала поиска нажмите \"Поиск пассажира\"",
                                 reply_markup=markup_menu)
                trip_num = 0
                break

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

                break

            trip_num = trip_num + 1
'''


@bot.message_handler(func=lambda message: message.text == "Продолжить поиск")
def continue_search(message):
    count, num = Trip.continue_search(message)
    location_drive(message, num, count)


def accept_trip_drive(message, order_num):
    global trip
    global chat_id_passenger
    global chat_id_drive
    chat_id_drive = message.chat.id
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

        rows = cur.fetchall()[order_num]

    result = float('{:.2f}'.format(geodesic((rows[3], rows[4]), (lon_dr, lat_dr)).km))
    trip = ('Откуда: ' + rows[0] + '\nКуда: ' + rows[1] + '\nЦена: ' + str(rows[2]) + '\nРастояние: ' + str(
        result)
            + ' КМ\n\n')
    chat_id_passenger = int(rows[5])

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_trip_dr')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_trip_dr')
    keyboard.add(key_no)

    bot.send_message(message.chat.id, trip, reply_markup=keyboard)


def time_arrival_drive(message):
    keyboard = types.InlineKeyboardMarkup()
    key_time1 = types.InlineKeyboardButton(text='1 Мин', callback_data='1_time')
    keyboard.add(key_time1)
    key_time3 = types.InlineKeyboardButton(text='3 Мин', callback_data='3_time')
    keyboard.add(key_time3)
    key_time5 = types.InlineKeyboardButton(text='5 Мин', callback_data='5_time')
    keyboard.add(key_time5)
    key_time10 = types.InlineKeyboardButton(text='10 Мин', callback_data='10_time')
    keyboard.add(key_time10)
    request = trip + "\n\nЧерез сколько времени будите" + '\n\n'
    bot.edit_message_text(request, message.chat.id, message.message_id)
    bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=keyboard)


def accepted_teip_drive(message, time_arrival):
    keyboard = types.InlineKeyboardMarkup()
    key_arrived = types.InlineKeyboardButton(text='Прибыл на место', callback_data='arrived')
    keyboard.add(key_arrived)
    key_cancel = types.InlineKeyboardButton(text='Отменить заказ', callback_data='to_cancel')
    keyboard.add(key_cancel)
    key_cancel = types.InlineKeyboardButton(text='Заказ выполнен', callback_data='fulfilled')
    keyboard.add(key_cancel)
    request = trip + '\n\nПрибудите через ' + str(time_arrival) + ' мин.' + '\n\n'
    bot.edit_message_text(request, message.chat.id, message.message_id)
    bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=keyboard)


### Конец поиска пассажира

###cursor.close()
###conn.close()

bot.polling(none_stop=False, interval=0, timeout=20)
