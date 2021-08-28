import csv
import os
from datetime import datetime

from bl.const import users_todo, csv_dir, file_path
from bl.remove_initial_keyboard import remove_initial_keyboard, render_yes_now_keyboard, render_initial_keyboard
from bot import bot


def process_add_todo(messege):
    user_id = messege.from_user.id
    users_todo[user_id] = {"user_id": user_id}
    remove_initial_keyboard(user_id, "Введите текст заметки")
    bot.register_next_step_handler(messege, get_text_todo)

def get_text_todo(messege):
    user_id = messege.from_user.id
    text_todo = messege.text.title()
    # bot.send_message(user_id, f"{text_todo}")

    if text_todo:
        users_todo[user_id]["text"] = text_todo

        bot.send_message(user_id, "Введи дату заметки в формате dd/mm/yyyy")
        bot.register_next_step_handler(messege, get_date_todo)
    else:
        bot.send_message(user_id, "Текст заметки не должен быть пустым!")
        bot.register_next_step_handler(messege, get_text_todo)

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
        question = f"Ты создал заметку с текстом \"{todo_text}\" на дату {todo_date}. Верно?"
        render_yes_now_keyboard(user_id, question, "to")
    except ValueError:
        bot.send_message(user_id, "Введи дату корректно!")
        bot.register_next_step_handler(messege, get_date_todo)

@bot.callback_query_handler(func=lambda call: call.data.startswith("to_"))
def callback_worker(call):
    user_id = call.from_user.id
    if call.data == "to_yes":
        bot.send_message(user_id, "Отлично, сейчас сделаю заметку!")

        fieldnames = ["user_id", "text", "date"]

        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)

        if not os.path.isfile(file_path):
            with open(file_path, "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames)
                writer.writeheader()

        with open(file_path, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames)

            user_todo = users_todo[user_id]
            writer.writerow(user_todo)

        bot.send_message(user_id, "Готово!")

    elif all.data == "to_no":
        # remove user
        users_todo.pop(user_id, None)
        render_initial_keyboard(user_id)
