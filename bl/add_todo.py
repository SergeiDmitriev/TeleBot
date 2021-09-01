import sqlite3
import os
from datetime import datetime

from bl.const import db_file_user_todo
from bl.remove_initial_keyboard import remove_initial_keyboard, render_yes_now_keyboard, render_initial_keyboard
from bot import bot

users_todo = {}
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
        date_todo = datetime.strptime(text_date_todo, "%d/%m/%Y").date()
        users_todo[user_id]["date_todo"] = date_todo

        todo_text = users_todo[user_id]["text"]
        todo_date = users_todo[user_id]["date_todo"]
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

        try:
            sqlite_connection = sqlite3.connect(db_file_user_todo)

        except sqlite3.Error as error:
            print('Ошибка подключения', error)

        command = """
            CREATE TABLE IF NOT EXISTS user_todo(
                user_id INTEGER,
                text VARCHAR(255) NOT NULL,
                date_todo DATE NOT NULL
            );
        """

        with sqlite_connection as conn:
            cur = conn.cursor()
            cur.execute(command)

        command = """
            INSERT INTO user_todo(user_id, text, date_todo)
            VALUES (:user_id, :text, :date_todo)
        """

        with sqlite_connection as conn:
            cur = sqlite_connection.cursor()
            cur.execute(command, users_todo[user_id])

        bot.send_message(user_id, "Готово!")

    elif all.data == "to_no":
        # remove user
        users_todo.pop(user_id, None)
        render_initial_keyboard(user_id)
