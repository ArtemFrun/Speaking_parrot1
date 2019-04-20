#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3
import customData
import Trip

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
        '''CREATE TABLE trip (dispatch TEXT, expectation TEXT, price INTEGER, lon_pas FLOAT, lat_pas FLOAT, chat_id INTEGER, status INTEGER)''')
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
    global chat_id
    global user_id
    user_id = 0
    chat_id = message.chat.id
    name = message.text
    bot.send_message(message.chat.id, 'Введите Фамилию')
    bot.register_next_step_handler(message, get_surname_dr)


def get_surname_dr(message):
    global surname
    surname = message.text
    bot.send_message(message.chat.id, 'Цвет автомобиля' + name)
    bot.register_next_step_handler(message, get_color_car)


def get_color_car(message):
    global color_car
    color_car = message.text
    bot.send_message(message.chat.id, 'Номер автомобиля' + name)
    bot.register_next_step_handler(message, get_number_car)


def get_number_car(message):
    global number_car
    number_car = message.text
    bot.send_message(message.chat.id, 'Марка автомобиля' + name)
    bot.register_next_step_handler(message, get_car_model)


def get_car_model(message):
    global car_model
    car_model = message.text
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_pas_dr')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_pas_dr')
    keyboard.add(key_no)
    info_reg_pas = 'Тебя зовут ' + name + ' ' + surname + ', номер телефона: ' + str(phone) + \
                   '. У тебя автомобиль' + car_model + ', номерной знак: ' +  number_car + \
                   ', цвет: ' + color_car + ' ?'
    bot.send_message(message.from_user.id, text=info_reg_pas, reply_markup=keyboard)



def get_reg_dr(message):
    info = [name, surname, phone, chat_id, user_id, color_car, number_car, car_model]
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
    if message.text == "Начать поездку":
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                         reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=['location'])
def location(message):
    global lon_pas
    global lat_pas
    lon_pas = message.location.longitude
    lat_pas = message.location.latitude
    bot.send_message(message.chat.id, "Введите адрес от куда будем ехать. Улица, дом, падезд.")
    bot.register_next_step_handler(message, arrivel)


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
    chat_id = message.chat.id
    price = int(message.text)
    bot.send_message(message.chat.id, "Поиск машины")
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отменить")
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Для отмены нажмите кнопку... Отменить ", reply_markup=keyboard)
    Trip.trip_pas(dispatch, expectation, price, lon_pas, lat_pas, chat_id)
    bot.register_next_step_handler(message, cancel_trip)


def cancel_trip(message):
    if message.text == "Отменить":
        bot.send_message(message.chat.id, "Для подтвержения отмены, наберите. Да")
        bot.register_next_step_handler(message, conf_cancel_trip)

def conf_cancel_trip(message):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Поиск отменен")
        global _chat_id
        _chat_id = message.chat.id
        Trip.cancel_trip_pas(_chat_id)
        markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  ###переход к поиску поездки
        btn_location = types.KeyboardButton('Начать поездку')
        markup_menu.add(btn_location)
        bot.send_message(message.chat.id, "Для поиска автомобиля нажмите на кнопкую. Начать поездку", reply_markup=markup_menu)



###Конец поездки пассажира



### Начало поиска пассажира
@bot.message_handler(func=lambda message: True)
def trip(message):
    if message.text == "Поиск пассажира":
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        keyboard.add(button_geo)
        bot.send_message(message.chat.id, "Отправите Ваше местоположение",
                         reply_markup=keyboard)


@bot.message_handler(func=lambda message: True, content_types=['location'])
def location(message):
    global lon_dr
    global lat_dr
    global _chat_id
    _chat_id = 0
    lon_dr = message.location.longitude
    lat_dr = message.location.latitude
    Trip.active_search_passenger(_chat_id)




### Конец поиска пассажира




###cursor.close()
###conn.close()

bot.polling(none_stop=False, interval=0, timeout=20)
