import telebot
from telebot import types
import sqlite3
import customData

bot = telebot.TeleBot(customData.TOKEN)


### прийом номера телефона запрос имени
def get_phone(message):
    global phone
    try:
        phone = int(message.text)
        bot.send_message(message.chat.id, 'Введите Имя')
        return
    except Exception:
         bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
         bot.register_next_step_handler(message, get_phone)

### прийом Имени запрос Фамилии
def get_name(message):
    global name
    global chat_id
    global user_id
    chat_id = message.chat.id
    user_id = 0
    name = message.text
    bot.send_message(message.chat.id, 'Введите Фамилию')
    return


###Для пассажира конец регистрации (прийом Фамилии)
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
    return

### прийом Фамилии запрос на цвет автомобиля
def get_surname_dr(message):
    global surname
    surname = message.text
    bot.send_message(message.chat.id, 'Цвет автомобиля')
    return

### прийом цвета автомобиля запрос автомобильного номера
def get_color_car(message):
    global color_car
    color_car = message.text
    bot.send_message(message.chat.id, 'Номер автомобиля')
    return

### прийом автомобильного номера запрос марки автомобиля
def get_number_car(message):
    global number_car
    number_car = message.text
    bot.send_message(message.chat.id, 'Марка автомобиля')
    return

### Конец регистрации водителя (прийом марки автомобиля)
def get_car_model(message):
    global car_model
    car_model = message.text
    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = types.InlineKeyboardButton(text='ДА', callback_data='YES_pas_dr')
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = types.InlineKeyboardButton(text='НЕТ', callback_data='NO_pas_dr')
    keyboard.add(key_no)
    info_reg_pas = 'Тебя зовут ' + name + ' ' + surname + ', \nномер телефона: ' + str(phone) + \
                   '\nАвтомобиль марки ' + car_model + '\nномерной знак: ' + number_car + \
                   '\nцвет: ' + color_car + ' ?'
    bot.send_message(message.from_user.id, text=info_reg_pas, reply_markup=keyboard)
    return


###Запись данных пассажира в БД
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
    bot.send_message(message.chat.id, "Регистрация успешна. Для на чала поездки нажмите кнопку \"Начать поездку\"",
                     reply_markup=markup_menu)
    return



###Запись данных водителя в БД
def get_reg_dr(message):
    info = [name, surname, phone, chat_id, user_id, color_car, number_car, car_model]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO drive VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)',(info))
    con.commit()
    markup_menu = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  ###переход к поиску поездки
    btn_start = types.KeyboardButton(text='Поиск пассажира')
    markup_menu.add(btn_start)
    bot.send_message(message.chat.id, "Регистрация успешна. Для поска пассажиров нажмите кнопу \"Поиск пассажира\"",
                     reply_markup=markup_menu)
    return
