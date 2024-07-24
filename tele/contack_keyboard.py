from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton("Share Contact", request_contact=True)
keyboard.add(button)