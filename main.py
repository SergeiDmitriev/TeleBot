from bl.add_todo import process_add_todo
from bl.get_todo import process_get_todo
from bl.models import create_bases
from bl.registration import process_registration
from bl.common import render_initial_keyboard, render_yes_now_keyboard
from bot import bot


@bot.message_handler(content_types=["text"])
def start(message):
    user_id = message.from_user.id
    if message.text == "Регистрация":
        process_registration(message)
    elif message.text == "TODO":
        process_add_todo(message)
    elif message.text == "Get TODO":
        process_get_todo(message)
    else:
        render_initial_keyboard(user_id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
    create_bases()