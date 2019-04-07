#!/usr/bin/env python
import telebot
from telebot.types import Message

TOKEN = '811665504:AAF7kaodvDeKyaiZErf-Yd2zyZ0walWbK2I'

bot = telebot.TeleBot(TOKEN)



@bot.message_handler(func=lambda m: True)
def echo_all(message: Message):
	bot.reply_to(message, message.text)



@bot.message_handler(content_types=['sticker'])
def echo_sticker(message: Message):
    STICKER_ID = message.sticker.file_id
    bot.send_sticker(message.chat.id, STICKER_ID)

@bot.message_handler(content_types=['photo'])
def echo_photo(message: Message):
    PHOTO_ID = message.photo[-1].file_id
    bot.send_photo(message.chat.id, PHOTO_ID)

@bot.message_handler(content_types=['video'])
def echo_video(message:Message):
    VIDEO_ID = message.video.file_id
    bot.send_video(message.chat.id, VIDEO_ID)

@bot.message_handler(content_types=['audio'])
def echo_audio(message: Message):
    AUDIO_ID = message.audio.file_id
    bot.send_audio(message.chat.id, AUDIO_ID)

bot.polling(none_stop=False, interval=0, timeout=20)