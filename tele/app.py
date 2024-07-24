import os
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
from contack_keyboard import keyboard
from aiogram.utils import executor
from db import Database
from custom_storage import CustomMemoryStorage
from functools import wraps
from aiogram import types
import logging
from dotenv import load_dotenv
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
storage = CustomMemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)


class NewCargo(StatesGroup):
    pickup_location = State()
    delivery_location = State()
    cargo_details = State()
    phone_number = State()

class UserRegister(StatesGroup):
    username = State()
    password = State()
    phone_number = State()



@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("""
            Welcome to the Cargo Bot!
            Use /new_cargo to create a new cargo order.
            Use /login to register your cargo
            Use /delivers all delivers list""")


@dp.message_handler(commands=['new_cargo'])
async def new_cargo(message: types.Message):
    await message.reply("Please provide the pickup location.")
    await NewCargo.pickup_location.set()


@dp.message_handler(commands=['login'])
async def new_user(message: types.Message):
    await message.reply("Please username")
    await UserRegister.username.set()


ADMIN_USER_IDS = [2127518090,]
def admin_only(func):
    @wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        if message.from_user.id not in ADMIN_USER_IDS:
            await message.reply("You are not authorized to use this command.")
            return
        return await func(message, *args, **kwargs)
    return wrapped


@dp.message_handler(commands=['delivers'])
@admin_only
async def delivers_list(message: types.Message):
    response = requests.get('http://localhost:8000/api/users/')
    users = response.json()
    if not users:
        await message.reply("No users found.")

    for user in users:
        user_info = f"Username: {user['username']}\nPhone: {user.get('phone_number', 'N/A')}\nEmail: {user['email']}\n"
        await message.reply(user_info)

    await message.reply("""
                Welcome to the Cargo Bot!
                Use /new_cargo to create a new cargo order.
                Use /login to register your cargo
                Use /delivers all delivers list""")


@dp.message_handler(state=UserRegister.username, content_types=types.ContentType.TEXT)
async def new_user_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = message.text
    await UserRegister.next()
    await message.reply("Please Password")


@dp.message_handler(state=UserRegister.password, content_types=types.ContentType.TEXT)
async def new_user_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
    await UserRegister.next()
    await message.reply("Please phone number", reply_markup=keyboard)


@dp.message_handler(state=UserRegister.phone_number, content_types=types.ContentType.CONTACT)
async def new_user_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number
        # await Database.user_register(username=data['username'], password=data['password'], phone_number=data['phone_number'])
        print(f">>>>>>>>>>>>>>>>>>>>>>>>")

    response = requests.post(
        'http://localhost:8000/api/users/register/',

        data=json.dumps({
            "username": data['username'],
            "password": data['password'],
            "phone_number": data['phone_number']
        }),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 201:
        await message.reply("Cargo order created successfully!", reply_markup=types.ReplyKeyboardRemove())

    else:
        await message.reply("Failed to create cargo order.", reply_markup=types.ReplyKeyboardRemove())

    logging.info(f"Finishing state for chat {message.chat.id}, user {message.from_user.id}")
    await state.finish()
    await message.reply(
        "Welcome to the Cargo Bot!\nUse /new_cargo to create a new cargo order.\n Use /login to register your cargo")


# >>>>>>>>>>>>>>>>>>>>>>> Cargo <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


@dp.message_handler(state=NewCargo.pickup_location, content_types=types.ContentType.TEXT)
async def process_pickup_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['pickup_location'] = message.text
    await NewCargo.next()
    await message.reply("Please provide the delivery location.")

@dp.message_handler(state=NewCargo.delivery_location, content_types=types.ContentType.TEXT)
async def process_delivery_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['delivery_location'] = message.text
    await NewCargo.next()
    # Create a button to share the contact
    await message.reply("Please provide the cargo details.")


# print(f"__________________________________________{data["phone_number"]}")


@dp.message_handler(state=NewCargo.cargo_details, content_types=ContentType.TEXT)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cargo_details'] = message.text
    await NewCargo.next()
    await message.reply("Please share your contact number.", reply_markup=keyboard)


@dp.message_handler(state=NewCargo.phone_number, content_types=types.ContentType.CONTACT)
async def process_cargo_details(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number
        check_user = await Database.check_user(phone_number=data['phone_number'])
        print(f">>>>>>>>>>>>>>>>>>>>>>>>{check_user}")

    if check_user:
        response = requests.post(
            'http://localhost:8000/api/cargo/',

            data=json.dumps({
                "pickup_location": data['pickup_location'],
                "delivery_location": data['delivery_location'],
                "cargo_details": data['cargo_details'],
                "user": check_user[0]
            }),
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            await message.reply("Cargo order created successfully!", reply_markup=types.ReplyKeyboardRemove())

    else:
        await message.reply("Failed to create cargo order.", reply_markup=types.ReplyKeyboardRemove())

    logging.info(f"Finishing state for chat {message.chat.id}, user {message.from_user.id}")
    await state.finish()
    await message.reply("Use /new_cargo to create a new cargo order.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
