from secrets import choice
import telebot
import sqlite3
import base64

conn = sqlite3.connect('passwords.db', check_same_thread=False)
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


bot = telebot.TeleBot('5604209602:AAG0SdGNOp_Vki9A65GJRZM0fivkflp3UGw')


def encrypt(string):
    base = 'FVr0jGy6HpAveOwdzMxPlhBYgLZNDc7saJKR52W+CQo19bkIT4iEqumSU3tn8Xf'
    for _ in range(10):
        string += f'{choice(base)}'
    string_bytes = string.encode('ascii')
    base64_bytes = base64.b64encode(string_bytes)
    string_encrypted = base64_bytes.decode('ascii')
    return string_encrypted


def decrypt(string):
    base64_bytes = string.encode('ascii')
    string_bytes = base64.b64decode(base64_bytes)
    string_decrypted = string_bytes.decode('ascii')
    return string_decrypted[:-10]


@bot.message_handler(commands=['start'])
def starting(message):
    print(message.from_user.id)
    bot.send_message(message.from_user.id, 'Hello and welcome to the Password Keeper telegram bot!')


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.from_user.id,
                     'Here`s what the bot can do: \n'
                     '============================ \n'
                     '• /add_password <service name> - <password> - add a password to your very own secure database \n'
                     '============================ \n'
                     '• /delete_password <service name> - remove one of your passwords if it`s no longer needed \n'
                     '============================ \n'
                     '• /show_my_password <service> - see your password for a certain service \n'
                     '============================ \n'
                     '• /show_my_passwords - see the list of all your passwords \n'
                     '============================ \n'
                     '\n\n'
                     'If something goes wrong, please contact the developer: \n'
                     '@cat_dev_lol on telegram or @cat_dev on discord!'
                     )


@bot.message_handler(commands=['add_password'])
def add_password(message):
    msg_content = message.text.split(' ')[1:]
    service = ''
    password = ''
    for i in range(len(msg_content)):
        if msg_content[i] != '-':
            service += msg_content[i]
        else:
            break
    for j in range(i + 1, len(msg_content)):
        password += msg_content[j]

    check = cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{str(message.from_user.id)}", f"{service}")).fetchone()
    if check is None:
        cur.execute("INSERT INTO passwords VALUES (?,?,?)", (f"{str(message.from_user.id)}", f"{service}", f"{encrypt(password)}"))
        conn.commit()
        bot.send_message(message.from_user.id, f'Successfully added a password for {service} to your password database!')
    else:
        bot.send_message(message.from_user.id, f'Sorry, but it seems like you already have a password for {service} in your password database. The service name must be unique for every password!')


@bot.message_handler(commands=['remove_password'])
def remove_password(message):
    msg_content = message.text.split(' ')[1:]
    service = ''
    for i in range(len(msg_content)):
        service += msg_content[i]
    check = cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{str(message.from_user.id)}", f"{service}")).fetchone()
    if check is None:
        bot.send_message(message.from_user.id, f'Sorry, but it seems like you didn`t add a password for {service} to your password database so there`s no need to remove it!')
    else:
        cur.execute("DELETE FROM passwords WHERE user_id=? AND service=?", (f"{str(message.from_user.id)}", f"{service}"))
        conn.commit()
        bot.send_message(message.from_user.id, f'Successfully removed a password for {service} from your password database!')


@bot.message_handler(commands=['show_my_password'])
def show_1_pass(message):
    msg_content = message.text.split(' ')[1:]
    service = ''
    for i in range(len(msg_content)):
        service += msg_content[i]

    password = cur.execute("SELECT * FROM passwords WHERE user_id=? AND service=?", (f"{str(message.from_user.id)}", f"{service}")).fetchone()
    if password is None:
        bot.send_message(message.from_user.id, f'Sorry, but it seems like you don`t have a password for {service}!')
    else:
        bot.send_message(message.from_user.id, f'Your password for {service} is: {decrypt(password[2])}')


@bot.message_handler(commands=['show_my_passwords'])
def show_all_passes(message):
    check = cur.execute("SELECT * FROM passwords WHERE user_id=?", (f"{str(message.from_user.id)}",)).fetchone()
    if check is None:
        bot.send_message(message.from_user.id, f'Sorry, but it seems like you don`t have any passwords in your password database!')
    else:
        passes = cur.execute("SELECT * FROM passwords WHERE user_id=?", (f"{str(message.from_user.id)}",)).fetchall()
        string = 'Here`s the list of all your passwords: \n'
        for el in passes:
            string += '-' * 28 + '\n'
            string += f'• {el[1]}: {el[2]} \n'
            string += '-' * 28 + '\n'
        bot.send_message(message.from_user.id, f'{string}')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
