from ultralytics import YOLO
import cv2
import telebot
from telebot import types
import cv2
import torch
from PIL import Image
import numpy as np
import io
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

model = YOLO('best_v8n_new.pt')

def process_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    results = model(img)
    if len(results[0].boxes) == 0:  # Если ничего не найдено
        return None
    else:
      for r in results:
        im_array = r.plot()
        im = Image.fromarray(im_array[..., ::-1])

        return im

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне фотографию, и я обнаружу на ней дефекты 🥸")


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "⏳ Обрабатываю изображение...")
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        processed_img = process_image(downloaded_file)
        if processed_img is None:
          bot.reply_to(message, "Кажется, на этом фото никаких дефектов нет")
        else:
          bot.send_chat_action(message.chat.id, 'upload_photo')
          img_byte_arr = io.BytesIO()
          processed_img.save(img_byte_arr, format='JPEG')
          img_byte_arr.seek(0)


          bot.send_photo(message.chat.id, img_byte_arr, caption="🔍🧐 Вот что я обнаружил")

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

print("Бот запущен")
bot.polling()