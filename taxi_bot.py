#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3
import customData
import Trip
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
        '''CREATE TABLE trip (dispatch TEXT, expectation TEXT, price INTEGER, lon_pas FLOAT, lat_pas FLOAT, chat_id INTEGER, status_trip INTEGER, date_Create TEXT, data_seconds INTEGER)''')
except:
    pass
###Таблица регистрации водителей.
try:
    cursor.execute(
        '''CREATE TABLE drive (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER, color_car TEXT, number_car TEXT, car_model TEXT)''')
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


@bot.callback_query_handler(func=lambda call: True)
def handle_text(call):
    if call.data == "pas":
        bot.send_message(call.message.chat.id, "Номер телефона")
        bot.register_next_step_handler(call.message, get_phone)
    elif call.data == "dr":
        bot.send_message(call.message.chat.id, "Номер телефона")
        bot.register_next_step_handler(call.message, get_phone_dr)
    elif call.data == "YES_pas_reg":
        bot.send_message(call.message.chat.id, "Для завершения наберите. ОК")
        bot.register_next_step_handler(call.message, get_reg)
    elif call.data == "NO_pas_reg":
        bot.send_message(call.message.chat.id, "Номер телефона")
        bot.register_next_step_handler(call.message, get_phone)
    elif call.data == "YES_pas_dr":
        bot.send_message(call.message.chat.id, "Для завершения наберите. ОК")
        bot.register_next_step_handler(call.message, get_reg_dr)
    elif call.data == "NO_pas_dr":
        bot.send_message(call.message.chat.id, "Номер телефона")
        bot.register_next_step_handler(call.message, get_phone_dr)
    elif call.data == str(order1):
        bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
        bot.register_next_step_handler(call.message, accept_trip_drive(call.message, order1))
    elif call.data == str(order2):
        bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
        bot.register_next_step_handler(call.message, accept_trip_drive(call.message, order2))
    elif call.data == str(order3):
        bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
        bot.register_next_step_handler(call.message, accept_trip_drive(call.message, order3))
    elif call.data == str(order4):
        bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
        bot.register_next_step_handler(call.message, accept_trip_drive(call.message, order4))
    elif call.data == str(order4):
        bot.send_message(call.message.chat.id, "Хотите принять этот заказ?")
        bot.register_next_step_handler(call.message, accept_trip_drive(call.message, order4))
    elif call.data == "YES_trip_dr":
        bot.send_message(call.message.chat.id, "Через сколько времени будите")
        bot.register_next_step_handler(call.message, get_reg_dr)
    elif call.data == "NO_trip_dr":
        markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
        btn_search = types.KeyboardButton('Поиск пассажира')
        markup_menu.add(btn_search)
        bot.send_message(call.message.chat.id, "Для начала поиска нажмите \"Поиск пассажира\"", reply_markup=markup_menu)



###Регистрация пасажира
###Прийом номера телефона
def get_phone(message):
    global phone
    try:
        phone = int(message.text)
        bot.send_message(message.chat.id, 'Введите Имя')
        bot.register_next_step_handler(message, get_name)
    except Exception:
         bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
         bot.register_next_step_handler(message, get_phone)


###Прийом Имени
def get_name(message):
    global name
    global chat_id
    global user_id
    chat_id = message.chat.id
    user_id = 0
    name = message.text
    bot.send_message(message.chat.id, 'Введите Фамилию')
    bot.register_next_step_handler(message, get_surname)


###Прийом Фамилии
def get_surname(message):
    global surname
    global info_reg_pas
    surname = message.text
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_pas_reg')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_pas_reg')
    keyboard.add(key_no)
    info_reg_pas = 'Тебя зовут ' + name + ' ' + surname + ', номер телефона: ' + str(phone) + '?'
    bot.send_message(message.from_user.id, text=info_reg_pas, reply_markup=keyboard)





###Запись данных в БД.
def get_reg(message):
    info = [name, surname, phone, chat_id, user_id]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO passenger VALUES (?, ?, ?, ?, ?)',
                (info))
    con.commit()
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)     ###переход к поиску поездки
    btn_location = types.KeyboardButton('Начать поездку')
    markup_menu.add(btn_location)
    bot.send_message(message.chat.id, "Регистрация успешна.", reply_markup=markup_menu)
###Конец регистрации пасажира




###Регистрация водителя
def get_phone_dr (message):
    global phone
    try:
        phone = int(message.text)
        bot.send_message(message.chat.id, 'Введите Имя')
        bot.register_next_step_handler(message, get_name_dr)
    except Exception:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, get_phone)



def get_name_dr(message):
    global name
    global chat_id_dr
    global user_id
    user_id = 0
    chat_id_dr = message.chat.id
    name = message.text
    bot.send_message(message.chat.id, 'Введите Фамилию')
    bot.register_next_step_handler(message, get_surname_dr)


def get_surname_dr(message):
    global surname
    surname = message.text
    bot.send_message(message.chat.id, 'Цвет автомобиля')
    bot.register_next_step_handler(message, get_color_car)


def get_color_car(message):
    global color_car
    color_car = message.text
    bot.send_message(message.chat.id, 'Номер автомобиля')
    bot.register_next_step_handler(message, get_number_car)


def get_number_car(message):
    global number_car
    number_car = message.text
    bot.send_message(message.chat.id, 'Марка автомобиля')
    bot.register_next_step_handler(message, get_car_model)


def get_car_model(message):
    global car_model
    car_model = message.text
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_pas_dr')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_pas_dr')
    keyboard.add(key_no)
    info_reg_pas = 'Тебя зовут ' + name + ' ' + surname + ', \nномер телефона: ' + str(phone) + \
                   '\nАвтомобиль марки ' + car_model + '\nномерной знак: ' +  number_car + \
                   '\nцвет: ' + color_car + ' ?'
    bot.send_message(message.from_user.id, text=info_reg_pas, reply_markup=keyboard)



def get_reg_dr(message):
    info = [name, surname, phone, chat_id_dr, user_id, color_car, number_car, car_model]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO drive VALUES (?, ?, ?, ?, ?, ?, ?, ?)',(info))
    con.commit()
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
    btn_location = types.KeyboardButton('Поиск пассажира')
    markup_menu.add(btn_location)
    bot.send_message(message.chat.id, "Регистрация успешна.", reply_markup=markup_menu)
###Конец регистрации водителя



### Начало поездки пасажира

@bot.message_handler(func=lambda message: True)
def trip(message):
    global type
    if message.text == "Начать поездку":
        type = 'passenger'
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                         reply_markup=keyboard)
    elif message.text == "Поиск пассажира":
        type = 'drive'
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                         reply_markup=keyboard)

###Передача геоданых
@bot.message_handler(func=lambda message: True, content_types=['location'])
def location_pas(message):
    if (type == 'passenger'):
        global lon_pas
        global lat_pas
        lon_pas = message.location.longitude
        lat_pas = message.location.latitude
        bot.send_message(message.chat.id, "Введите адрес от куда будем ехать. Улица, дом, падезд.")
        bot.register_next_step_handler(message, arrivel)
    elif(type == 'drive'):
        global lon_dr
        global lat_dr
        lon_dr = message.location.longitude
        lat_dr = message.location.latitude
        bot.register_next_step_handler(message, location_drive(message, 0, 0))



### Для пассажира
def arrivel(message):
    global dispatch
    dispatch = message.text
    bot.send_message(message.chat.id, "Введите адрес куда едим. Улица, дом.")
    bot.register_next_step_handler(message, expectation)


def expectation(message):
    global expectation
    expectation = message.text
    bot.send_message(message.chat.id, "Введите суму")
    bot.register_next_step_handler(message, trip_price)


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


def cancel_trip(message):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Для подтвержения отмены, наберите. Да")
        bot.register_next_step_handler(message, conf_cancel_trip)


def conf_cancel_trip(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Поиск отменен")
        Trip.cancel_trip_pas(chat_id)
        markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
        btn_location = types.KeyboardButton('Начать поездку')
        markup_menu.add(btn_location)
        bot.send_message(message.chat.id, "Для поиска автомобиля нажмите на кнопкую. Начать поездку", reply_markup=markup_menu)



###Конец поездки пассажира



### Начало поиска пассажира


def location_drive(message, num, count):
     global keyboards
     global trip_num
     global order1
     global order2
     global order3
     global order4
     global order5
     global counter
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
         while True:
             row = cur.fetchone()

             if row == None:
                 markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
                 btn_search = types.KeyboardButton('Поиск пассажира')
                 markup_menu.add(btn_search)
                 bot.send_message(message.chat.id, "Больше нету заказов. Для начала поиска нажмите \"Поиск пассажира\"",
                                  reply_markup=markup_menu)
                 trip_num = 0
                 break

             result = float('{:.2f}'.format(geodesic((row[3], row[4]), (lon_dr, lat_dr)).km))

             if trip_num == 0 + counter:
                 order1 = trip_num
                 keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                 key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data=str(order1))
                 keyboard.add(key_yes)
             elif trip_num == 1 + counter:
                 order2 = trip_num
                 keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                 key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data=str(order2))
                 keyboard.add(key_yes)
             elif trip_num == 2 + counter:
                 order3 = trip_num
                 keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                 key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data=str(order3))
                 keyboard.add(key_yes)
             elif trip_num == 3 + counter:
                 order4 = trip_num
                 keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                 key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data=str(order4))
                 keyboard.add(key_yes)
             elif trip_num == 4 + counter:
                 order5 = trip_num
                 keyboard = types.InlineKeyboardMarkup()  # клавиатура принятия заказа
                 key_yes = types.InlineKeyboardButton(text='Принять заказ', callback_data=str(order5))
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
                 bot.register_next_step_handler(message, continue_search(message, trip_num, counter))
                 break

             trip_num = trip_num + 1


def continue_search(message, num, count):
    if message.text == "Продолжить поиск":
        count += 5
        bot.register_next_step_handler(message, location_drive(message, num, count))




def accept_trip_drive(message, order_num):
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
            + ' КМ')

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_trip_dr')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_trip_dr')
    keyboard.add(key_no)

    bot.send_message(message.chat.id, trip, reply_markup=keyboard)



### Конец поиска пассажира


###cursor.close()
###conn.close()

bot.polling(none_stop=False, interval=0, timeout=20)
