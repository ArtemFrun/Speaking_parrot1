import telebot
import sqlite3
import customData


bot = telebot.TeleBot(customData.TOKEN)
conn = sqlite3.connect('mydb.sqlite')
cursor = conn.cursor()


def trip_pas(dispatch, expectation, price, lon_pas, lat_pas, chat_id):
    global status
    status = 1
    info_trip = [dispatch, expectation, price, lon_pas, lat_pas, chat_id, status]
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('INSERT INTO trip VALUES (?, ?, ?, ?, ?, ?, ?)',(info_trip))
    con.commit()
    return


def cancel_trip_pas(_status):
    with sqlite3.connect("mydb.sqlite") as con:
        cur = con.cursor()
    cur.execute('UPDATE trip SET status="4"')
    con.commit()
    return





