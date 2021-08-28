import os

users = {}
users_todo = {}
todo_from_file = list()

csv_dir = os.path.join("TODOInformation", "csv")
file_path = os.path.join(csv_dir, "todos.csv")

DATE_FORMAT = "%d/%m/%Y"
