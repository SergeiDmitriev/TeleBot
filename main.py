import telebot
import json
import os
from telebot import types
from functools import wraps
from datetime import datetime

API_TOKEN = "1917167207:AAFt7FiuHG4LfwiSQTg34rUwu4aLlyjxv0A"

bot = telebot.TeleBot(API_TOKEN)

users = {}
users_todo = {}


def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)


@bot.message_handler(content_types=["text"])
def start(message):
    user_id = message.from_user.id
    if message.text == "Регистрация":
        # create empty user
        users[user_id] = {}
        remove_initial_keyboard(user_id, "Как тебя зовут?")
        bot.register_next_step_handler(message, get_name)
    elif message.text == "TODO":
        users_todo[user_id] = {}
        remove_initial_keyboard(user_id, "Введите текст заметки")
        bot.register_next_step_handler(message, get_text_todo)

    # elif message.text == "Test":
    #     remove_initial_keyboard(user_id, "Test")
    else:
        render_initial_keyboard(user_id)

def get_text_todo(message):
    user_id = message.from_user.id
    text_todo = message.text.title()
    # bot.send_message(user_id, f"{text_todo}")

    if text_todo:
        users_todo[user_id]["text"] = text_todo

        bot.send_message(user_id, "Введи дату заметки в формате dd/mm/yyyy")
        bot.register_next_step_handler(message, get_date_todo)
    else:
        bot.send_message(user_id, "Текст заметки не должен быть пустым!")
        bot.register_next_step_handler(message, get_text_todo)

def get_date_todo(messege):
    user_id = messege.from_user.id
    text_date_todo = messege.text.title()
    # bot.send_message(user_id, f"{text_date_todo}")
    # bot.send_message(user_id, f"{type(text_date_todo)}")

    try:
        date_todo = datetime.strptime(text_date_todo, "%d/%m/%Y")
        users_todo[user_id]["date"] = text_date_todo

        todo_text = users_todo[user_id]["text"]
        todo_date = users_todo[user_id]["date"]
        question = f"Ты создал заметку с тексттом \"{todo_text}\" на дату {todo_date}. Верно?"
        render_yes_now_keyboard(user_id, question, "to")
    except:
        bot.send_message(user_id, "Введи дату корректно!")
        bot.register_next_step_handler(messege, get_date_todo)

def get_name(message):
    user_id = message.from_user.id
    name = message.text.title()
    if is_valid_name_surname(name):
        users[user_id]["name"] = name.title()
        bot.send_message(user_id, "Какая у тебя фамилия?")
        bot.register_next_step_handler(message, get_surname)
    else:
        bot.send_message(user_id, "Введите корректное имя")
        bot.register_next_step_handler(message, get_name)


def get_surname(message):
    surname = message.text
    user_id = message.from_user.id
    if is_valid_name_surname(surname):
        users[user_id]["surname"] = surname.title()
        bot.send_message(user_id, "Введите номер телефона")
        bot.register_next_step_handler(message, get_phone_number)
    else:
        bot.send_message(user_id, "Введите корректную фамилию")
        bot.register_next_step_handler(message, get_surname)

def change_phone_number(func):
    @wraps(func)
    def wrapper(message):
        phone_number = message.text.title()
        user_id = message.from_user.id

        phone_number_length = 9
        phone_number_9 = phone_number[-phone_number_length:]
        full_phone_number = f"+375{phone_number_9}"
        users[user_id]["phone_number"] = full_phone_number

        return func(message)
    return wrapper

@change_phone_number
def get_phone_number(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Сколько тебе лет?")
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    age_text = message.text
    user_id = message.from_user.id
    if age_text.isdigit():
        age = int(age_text)
        if not 10 <= age <= 100:
            bot.send_message(user_id, "Введите реальный возраст, пожалуйста")
            bot.register_next_step_handler(message, get_age)
        else:
            users[user_id]["age"] = int(age)
            name = users[user_id]["name"]
            surname = users[user_id]["surname"]
            phone_number = users[user_id]["phone_number"]
            question = f"Тебе {age} лет и тебя зовут {name} {surname}, а твой номер телефона {phone_number}?"
            render_yes_now_keyboard(user_id, question, "reg")
    else:
        bot.send_message(user_id, "Введите цифрами, пожалуйста")
        bot.register_next_step_handler(message, get_age)


@bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
@bot.callback_query_handler(func=lambda call: call.data.startswith("to_"))
def callback_worker(call):
    user_id = call.from_user.id
    if call.data == "reg_yes":
        bot.send_message(user_id, "Спасибо, я запомню!")
        json_dir = "InformationAboutUsers"
        file_path = os.path.join(json_dir, "users.json")
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        with open(file_path, "w") as json_file:
            json.dump(users, json_file, indent=4, sort_keys=True)

        bot.send_message(user_id, "А лучше запишу в формате .json)")
        # pretend that we save in database
    elif call.data == "to_yes":
        bot.send_message(user_id, "Отлично, сейчас сделаю заметку!")

        json_dir = "TODOInformation"
        file_path = os.path.join(json_dir, "todos.json")
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        with open(file_path, "w") as json_file:
            json.dump(users_todo, json_file, indent=4, sort_keys=True)
    elif call.data == "reg_no" or all.data == "to_no":
        # remove user
        users.pop(user_id, None)
        render_initial_keyboard(user_id)


def render_yes_now_keyboard(user_id: int, question: str, prefix: str):
    keyboard = types.InlineKeyboardMarkup()

    key_yes = types.InlineKeyboardButton(text="Да", callback_data=f"{prefix}_yes")
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text="Нет", callback_data=f"{prefix}_no")
    keyboard.add(key_no)
    bot.send_message(user_id, text=question, reply_markup=keyboard)


def render_initial_keyboard(user_id: int):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    register_button = types.KeyboardButton("Регистрация")
    todo_button = types.KeyboardButton("TODO")
    # test_button = types.KeyboardButton("Test")
    keyboard.add(register_button, todo_button)
    bot.send_message(user_id, "Выберите действие", reply_markup=keyboard)


def remove_initial_keyboard(user_id: int, message: str):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(user_id, message, reply_markup=keyboard)


if __name__ == "__main__":
    bot.polling(none_stop=True)