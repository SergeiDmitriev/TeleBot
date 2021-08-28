import json
import os
from functools import wraps

from bl.const import users
from bl.remove_initial_keyboard import remove_initial_keyboard, render_yes_now_keyboard, render_initial_keyboard
from bot import bot


def process_registration(message):
    # create empty user
    user_id = message.from_user.id

    users[user_id] = {}
    remove_initial_keyboard(user_id, "Как тебя зовут?")
    bot.register_next_step_handler(message, get_name)

def is_valid_name_surname(name_surname):
    return not (" " in name_surname or len(name_surname) < 2)

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

def write_file_json(json_dir, file_name, data_set):
    file_path = os.path.join(json_dir, f"{file_name}.json")
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    with open(file_path, "w") as json_file:
        json.dump(data_set, json_file, indent=4, sort_keys=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
def callback_worker(call):
    user_id = call.from_user.id
    if call.data == "reg_yes":
        bot.send_message(user_id, "Спасибо, я запомню!")

        json_dir = "InformationAboutUsers"
        file_name = "users"
        write_file_json(json_dir, file_name, users)

        bot.send_message(user_id, "А лучше запишу в формате .json)")
        # pretend that we save in database

    elif call.data == "reg_no":
        # remove user
        users.pop(user_id, None)
        render_initial_keyboard(user_id)

