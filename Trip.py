import telebot
import sqlite3
import customData


bot = telebot.TeleBot(customData.TOKEN)
conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()

###Создание поездки
def trip_pas(dispatch, expectation, price, lon_pas, lat_pas, chat_id):
    global status
    status = 1
    info_trip = [dispatch, expectation, price, lon_pas, lat_pas, chat_id, status]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?)',(info_trip))
    con.commit()
    return

###Отмена поездки пасажиром
def cancel_trip_pas(_chat_id):
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('UPDATE trip SET status="4" WHERE chat_id=_chat_id AND status="1"')
    con.commit()
    return


###Отображение активных заказов
def active_search_passenger(_chat_id):
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    active_trip = 'SELECT * FROM trip WHERE chat_id!=_chat_id AND status="1"'
    cur.execute(active_trip)
    active_search =





