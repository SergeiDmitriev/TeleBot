import csv
import os

from datetime import datetime

from bl.const import todo_from_file, DATE_FORMAT
from bl.remove_initial_keyboard import remove_initial_keyboard
from bot import bot


def process_get_todo(message):
    user_id = message.from_user.id
    get_todo_file_from_user_id(user_id)

    remove_initial_keyboard(user_id, "Введи дату заметки в формате dd/mm/yyyy")
    bot.register_next_step_handler(message, get_text_todo_from_file)

def get_todo_file_from_user_id(user_id):
    csv_dir = os.path.join("TODOInformation", "csv")
    file_path = os.path.join(csv_dir, "todos.csv")
    todo_from_file.clear()

    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for csv_str in reader:
            if csv_str["user_id"] == str(user_id):
                todo_from_file.append(csv_str)

def get_text_todo_from_file(message):
    user_id = message.from_user.id
    if todo_from_file:
        try:
            text_date_todo = message.text.title()
            date_todo = datetime.strptime(text_date_todo, DATE_FORMAT)
            required_data = list(find_all_by_key(todo_from_file, text_date_todo))

            if required_data:
                bot.send_message(user_id, f"На дату {text_date_todo} найдены следующие заметки:")

                counter = 1
                for required in required_data:
                    required_str = required["text"]

                    bot.send_message(user_id, f"{counter}. {required_str}")
                    counter += 1
            else:
                bot.send_message(user_id, f"На дату {text_date_todo} нет заметок")
        except ValueError:
            bot.send_message(user_id, "Введи дату корректно!")
            bot.register_next_step_handler(messege, get_text_todo_from_file)

def find_all_by_key(iterable, date_now):
    return (dict_ for dict_ in iterable
            if date_now == dict_["date"])
