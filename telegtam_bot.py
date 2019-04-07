#!/usr/bin/env python
import telebot
from telebot.types import Message

TOKEN = '811665504:AAF7kaodvDeKyaiZErf-Yd2zyZ0walWbK2I'


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda m: True)
def echo_all(message: Message):
	bot.reply_to(message, message.text)


bot.polling(timeout=60)
