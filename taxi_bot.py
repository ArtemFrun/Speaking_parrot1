#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3

conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()

TOKEN = '811665504:AAF7kaodvDeKyaiZErf-Yd2zyZ0walWbK2I'

bot = telebot.TeleBot(TOKEN)

name = ''
surname = ''
phone = 0
chat_id = 0
user_id = 0


try:
    cursor.execute(
        '''CREATE TABLE passenger (user_name TEXT, surname TEXT, phone INTEGER, chat_id INTEGER, user_id INTEGER)''')
except:
    pass


@bot.message_handler(commands=['start', 'help'])
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
    global chat_id
    chat_id = message.chat.id
    surname = message.text
    bot.send_message(message.chat.id, 'OK')
    bot.register_next_step_handler(message, get_reg)


def get_reg(message):
    global phone
    global name
    global surname
    global chat_id
    global user_id
    chat_id = message.chat.id
    cursor.execute('INSERT INTO passenger VALUES (?, ?, ?, ?, ?)', (name, surname, phone, chat_id, user_id))
    conn.commit()


cursor.close()
conn.close()

bot.polling(none_stop=False, interval=0, timeout=20)
