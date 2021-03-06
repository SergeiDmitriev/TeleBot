import csv
import os
import sqlite3

from datetime import datetime

from bl.const import DATE_FORMAT, db_file_user_todo
from bl.remove_initial_keyboard import remove_initial_keyboard
from bot import bot


def process_get_todo(message):
    user_id = message.from_user.id

    remove_initial_keyboard(user_id, "Введи дату заметки в формате dd/mm/yyyy")
    bot.register_next_step_handler(message, get_text_todo_from_file)

def get_todo_file_from_user_id(user_id, date_todo):
    text_message = ""

    command = """
        SELECT text FROM user_todo
        WHERE user_id = :user_id
        AND date_todo = :date_todo
    """

    with sqlite3.connect(db_file_user_todo) as conn:
        cur = conn.cursor()
        result = cur.execute(command, {"user_id": user_id, "date_todo": date_todo})

        for num, res in enumerate(result.fetchall()):
            text_message = text_message + "\n" + str((num + 1)) + ". " + res[0]

    return text_message

def get_text_todo_from_file(message):
    user_id = message.from_user.id

    try:
        text_date_todo = message.text.title()
        date_todo = datetime.strptime(text_date_todo, DATE_FORMAT).date()
        text_message = get_todo_file_from_user_id(user_id, date_todo)

        if text_message:
            bot.send_message(user_id, f"На дату {text_date_todo} найдены следующие заметки:" + text_message)

        else:
            bot.send_message(user_id, f"На дату {text_date_todo} нет заметок")
    except ValueError:
        bot.send_message(user_id, "Введи дату корректно!")
        bot.register_next_step_handler(message, get_text_todo_from_file)
