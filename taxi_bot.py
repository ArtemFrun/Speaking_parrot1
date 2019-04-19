#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3
import customData

conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()

###, request_location=True
bot = telebot.TeleBot(customData.TOKEN)



try:
    cursor.execute(
        '''CREATE TABLE passenger (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER)''')
except:
    pass

try:
    cursor.execute(
        '''CREATE TABLE drive (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER, color_car TEXT, number_car TEXT, car_model TEXT)''')
except:
    pass

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

#Регистрация пасажира
def get_phone(message):
    global phone
    phone = int(message.text)
    bot.send_message(message.chat.id, 'Введите Имя')
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Введите Фамилию')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.chat.id, 'Тебя зовут' + name)
    bot.register_next_step_handler(message, get_reg)


def get_reg(message):
    global chat_id
    chat_id = message.chat.id
    user_id = 0
    info = [name, surname, phone, chat_id, user_id]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO passenger VALUES (?, ?, ?, ?, ?)',
                (info))
    con.commit()
    markup_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_location = types.KeyboardButton('Начать поездку')
    markup_menu.add(btn_location)
    bot.send_message(message.chat.id, "Регистрация успешна.", reply_markup=markup_menu)





#Регистрация водителя
def get_phone_dr (message):
    global phone
    phone = int(message.text)
    bot.send_message(message.chat.id, 'Введите Имя')
    bot.register_next_step_handler(message, get_name_dr)


def get_name_dr(message):
    global name
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
    bot.send_message(message.chat.id, 'ДА' + name)
    bot.register_next_step_handler(message, get_reg_dr)

def get_reg_dr(message):
    global chat_id
    chat_id = message.chat.id
    user_id = 0
    info = [name, surname, phone, chat_id, user_id, color_car, number_car, car_model]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO drive VALUES (?, ?, ?, ?, ?, ?, ?, ?)',(info))
    con.commit()


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

def arrivel (message):
    global dispatch
    dispatch = message.text
    bot.send_message(message.chat.id, "Введите адрес куда едим. Улица, дом.")
    bot.register_next_step_handler(message, expectation)

def expectation(message):
    global expectation
    expectation = message.text
    bot.send_message(message.chat.id, "Поиск машины")

###cursor.close()
###conn.close()

bot.polling(none_stop=False, interval=0, timeout=20)
