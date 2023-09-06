from secrets import choice
from markups import *
import telebot
import sqlite3
import base64


conn = sqlite3.connect('passwords.db', check_same_thread=False)  # you don't need to create the passwords.db file yourself
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS passwords
(
    user_id TEXT,
    service TEXT,
    password LONGTEXT
)
""")
conn.commit()
print('[Debug]: SQL connection acquired!')

with open('token.txt', 'r') as f:  # you need to create the token.txt file yourself
    bot = telebot.TeleBot(f.readline())


def my_encrypt(string):
    base = 'FVr0jGy6HpAveOwdzMxPlhBYgLZNDc7saJKR52W+CQo19bkIT4iEqumSU3tn8Xf'
    for _ in range(10):
        string += f'{choice(base)}'
    string_bytes = string.encode('ascii')
    base64_bytes = base64.b64encode(string_bytes)
    string_encrypted = base64_bytes.decode('ascii')
    return string_encrypted


def my_decrypt(string):
    base64_bytes = string.encode('ascii')
    string_bytes = base64.b64decode(base64_bytes)
    string_decrypted = string_bytes.decode('ascii')
    return string_decrypted[:-10]


@bot.message_handler(commands=['start'])
def starting(message):
    bot.send_message(message.from_user.id, "Hello and welcome to the Password Keeper telegram bot!")
    bot.send_message(message.from_user.id, "Now you can start working with the bot!", reply_markup=mk_1)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    match call.data:  # since python 3.10 match-case can be used instead of multiple elif's. works the same way as switch-case in java
        case "contacts":
            send_contacts(call.message.chat.id)
        case "add_password":
            start_adding_password(call.message.chat.id)
        case "remove_password":
            start_removing_password(call.message.chat.id)
        case "see_passwords":
            start_showing_passwords(call.message.chat.id)
        case "see_1_password":
            show_1_password_step1(call.message.chat.id)
        case "see_all_passwords":
            show_all_passwords(call.message.chat.id)


def send_contacts(usr_id):
    bot.send_message(usr_id, "If you believe the bot is not functioning as intended "
                             "or if you want to contribute to the project to make it better, here are the developer's contacts:\n"
                             "Discord: @cat_dev\n"
                             "Telegram: @cat_dev_lol",
                     reply_markup=mk_2)


def start_adding_password(usr_id):
    bot.send_message(usr_id, "Ok, let's add a password to your password list.")
    msg = bot.send_message(usr_id, "What service do you use this password for?"
                                   " (Keep in mind that you can only keep one password for each service."
                                   " If you use multiple accounts, add them as shown in this example: Amazon; Amazon1; Amazon2 etc.)")
    bot.register_next_step_handler(msg, adding_password_step2)


def adding_password_step2(message):
    if cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{message.from_user.id}", f"{message.text}")).fetchone() is not None:
        msg = bot.send_message(message.from_user.id, f"Sorry, but it seems like you already have a password for {message.text} in your password list!\n"
                                                     f"Try adding the password again with another service name!")
        bot.register_next_step_handler(msg, adding_password_step2)
    else:
        cur.execute("INSERT INTO passwords (user_id, service) VALUES (?,?)", (f"{message.from_user.id}", f"{message.text}"))
        conn.commit()
        msg = bot.send_message(message.from_user.id, f"Now, what is the password?"
                                                     f" (The bot will only store the password after it is encrypted so"
                                                     f" even if somebody gets it, it will be hard for them to decrypt correctly)")
        bot.register_next_step_handler(msg, adding_password_final_step, message.text)


def adding_password_final_step(message, service):
    cur.execute("UPDATE passwords SET password=? WHERE user_id=? AND service=?", (f"{my_encrypt(message.text)}", f"{message.from_user.id}", f"{service}"))
    conn.commit()
    bot.send_message(message.from_user.id, f"Added a password for {service} to your password list successfully!")
    bot.send_message(message.from_user.id, "Anything else you would like to do?", reply_markup=mk_1)


def start_removing_password(usr_id):
    bot.send_message(usr_id, "Ok, let's remove a password from your password list.")
    msg = bot.send_message(usr_id, "What service did you use this password for?")
    bot.register_next_step_handler(msg, removing_password_step2)


def removing_password_step2(message):
    if cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{message.from_user.id}", f"{message.text}")).fetchone() is None:
        bot.send_message(message.from_user.id, f"It seems like you didn't add a password for {message.text} to your password list before!")
    else:
        cur.execute("DELETE FROM passwords WHERE user_id=? AND service=?", (f"{message.from_user.id}", f"{message.text}"))
        conn.commit()
        bot.send_message(message.from_user.id, f"Removed a password for {message.text} from your password list successfully!")
    bot.send_message(message.from_user.id, "Anything else you would like to do?", reply_markup=mk_1)


def start_showing_passwords(usr_id):
    bot.send_message(usr_id, "Do you want to see your password for a given service or a list of all your passwords?", reply_markup=mk_3)


def show_1_password_step1(usr_id):
    msg = bot.send_message(usr_id, "Which of your services password do you want to see?")
    bot.register_next_step_handler(msg, show_1_password_step2)


def show_1_password_step2(message):
    if cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{message.from_user.id}", f"{message.text}")).fetchone() is None:
        bot.send_message(message.from_user.id, f"It seems like you don't have a password for {message.text} in your password list!")
    else:
        password = my_decrypt(cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{message.from_user.id}", f"{message.text}")).fetchone()[2])
        bot.send_message(message.from_user.id, f"Your password for {message.text} is: {password}")
    bot.send_message(message.from_user.id, "Anything else you would like to do?", reply_markup=mk_1)


def show_all_passwords(usr_id):
    if cur.execute("SELECT * FROM passwords WHERE user_id=?", (f"{usr_id}", )).fetchone() is None:
        bot.send_message(usr_id, f"It seems like you don't have any passwords in your password list!")
    else:
        password_list = "Your password list:\n"
        password_list += '-' * 28 + '\n'
        for el in cur.execute("SELECT * FROM passwords WHERE user_id=?", (f"{usr_id}", )).fetchall():
            password_list += f"Service: {el[1]}, Password: {my_decrypt(el[2])}\n"
            password_list += '-' * 28 + '\n'
        bot.send_message(usr_id, f"{password_list}")
    bot.send_message(usr_id, "Anything else you would like to do?", reply_markup=mk_1)


if __name__ == '__main__':
    print('[Debug]: Bot is running!')
    bot.polling(none_stop=True, interval=0)
