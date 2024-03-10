import sqlite3
import random
import time

import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText

# Размеры кнопок
recipient_1 = ''
recipient_2 = []
article_for_recipient_1 = ''
message_for_recipient_1 = ''
with sqlite3.connect("dat.db", check_same_thread=False) as db:
    cursor = db.cursor()

    query = """CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        user_id TEXT(30),
        user_name TEXT(30),
        login TEXT(30),
        password TEXT(30)
        );

        CREATE TABLE IF NOT EXISTS information(
        id INTEGER PRIMARY KEY,
        login TEXT(30),
        recipient TEXT(100),
        article TEXT(100),
        message TEXT(300)
    );
    """
    cursor.executescript(query)
bot = telebot.TeleBot('token')


def addition_users(user_id, user_name, login, password):
    cursor.execute("INSERT INTO users(user_id, user_name, login, password) VALUES(?, ?, ?, ?)",
                   [user_id, user_name, login, password])
    db.commit()


def addition_information(login, recipient, article, message):
    cursor.execute("INSERT INTO information(login, recipient, article, message) VALUES(?, ?, ?, ?)",
                   [login, recipient, article, message])
    db.commit()


def registered_users(message):
    registered_users = []
    kol = 0
    cursor.execute("SELECT user_id FROM users")
    a = cursor.fetchall()
    while len(a) != kol:
        b = a[kol]
        c = int(b[0])
        registered_users.append(c)
        kol += 1
    if message.from_user.id in registered_users:
        markup_3 = types.ReplyKeyboardMarkup()

        btn1 = types.KeyboardButton('Удалить учетную запись')
        btn2 = types.KeyboardButton('Выйти в главное меню')
        markup_3.row(btn1)
        markup_3.row(btn2)

        cursor.execute("SELECT login FROM users WHERE user_id = ?", [message.from_user.id])
        login = cursor.fetchall()[0]
        cursor.execute("SELECT password FROM users WHERE user_id = ?", [message.from_user.id])
        password = cursor.fetchall()[0]
        bot.send_message(message.chat.id,
                         f"Вы уже зарегестрированны\nВаш логин: {login[0]}\nВаш пароль: <tg-spoiler>{password[0]}</tg-spoiler>\nУдалить учетную запись/Выйти в главное меню",
                         parse_mode='html', reply_markup=markup_3)
        bot.register_next_step_handler(message, delete_or_log_in)
    else:
        input_login(message)


def delete_or_log_in(message):
    if message.text == "Удалить учетную запись":
        cursor.execute("DELETE FROM users WHERE user_id = ?", [message.from_user.id])
        start_for_log_in_and_registration(message)
    elif message.text == "Выйти в главное меню":
        bot.send_message(message.chat.id, "Переносим вас в главное меню")
        start_for_log_in_and_registration(message)


# Регистрация/Вход
@bot.message_handler(commands=['start'])
def start_for_log_in_and_registration(message):
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Зарегистрироваться')
    btn2 = types.KeyboardButton('Войти')
    markup.row(btn1)
    markup.row(btn2)

    bot.send_message(message.chat.id,
                     f'{message.from_user.first_name}, для использования бота вам нужно войти в учетную запись или создать её',
                     reply_markup=markup)

    bot.register_next_step_handler(message, click_on)


def click_on(message):
    if message.text == 'Войти':
        bot.send_message(message.chat.id,
                         'Введите ваш логин:', reply_markup=types.ReplyKeyboardRemove())

        bot.register_next_step_handler(message, check_login_for_log_in)
    elif message.text == "Зарегистрироваться":
        registered_users(message)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда!")
        start_for_log_in_and_registration(message)


def input_login(message):
    bot.send_message(message.chat.id, "Введите логин:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, check_login_for_registration)


def check_login_for_log_in(message):
    global login
    login = message.text
    cursor.execute("SELECT password FROM users WHERE login = ?", [login])
    if cursor.fetchall() is None:
        bot.send_message(message.chat.id, "Такого логина нет!")
        bot.register_next_step_handler(message, start_for_log_in_and_registration)


    else:
        bot.send_message(message.chat.id, "Введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_password_for_log_in)


def check_password_for_log_in(message):
    password = message.text
    cursor.execute("SELECT login FROM users WHERE password = ?", [password])
    a = cursor.fetchall()
    if a == []:
        bot.send_message(message.chat.id, "Неверный пароль!")
        start_for_log_in_and_registration(message)
    else:
        bot.send_message(message.chat.id, "Вы вошли в аккаунт!")
        the_most_main_start(message)


def choice_password_first_step(message):
    markup_2 = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Ввести пароль')
    btn2 = types.KeyboardButton('Сгенерировать пароль')
    markup_2.row(btn1)
    markup_2.row(btn2)

    bot.send_message(message.chat.id, f'Ввести пароль/Сгенерировать пароль',
                     reply_markup=markup_2)

    bot.register_next_step_handler(message, choice_password_second_step)


def choice_password_second_step(message):
    if message.text == "Ввести пароль":
        bot.send_message(message.chat.id, "Введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_password_for_registration)
    elif message.text == "Сгенерировать пароль":
        random_password_for_registration(message)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда!")
        start_for_log_in_and_registration(message)


def check_login_for_registration(message):
    global login_for_registration
    login_for_registration = message.text
    cursor.execute("SELECT login FROM users WHERE login = ?", [login_for_registration])
    if cursor.fetchall() != []:
        bot.reply_to(message, 'Этот логин уже занят!')
        start_for_log_in_and_registration(message)
    else:
        choice_password_first_step(message)


def check_password_for_registration(message):
    password = message.text
    kol = 0
    kol_2 = 0
    if len(password) >= 8:
        if password.isupper() == True:
            bot.send_message(message.chat.id, "В пароле должна быть хотя бы одна строчная буква!")
            start_for_log_in_and_registration(message)
        if password.islower() == True:
            bot.send_message(message.chat.id, "В пароле должна быть хотя бы одна заглавная буква!")
            start_for_log_in_and_registration(message)
        for i in password:
            if i == "0":
                kol += 1
            elif i == "1":
                kol += 1
            elif i == "2":
                kol += 1
            elif i == "3":
                kol += 1
            elif i == "4":
                kol += 1
            elif i == "5":
                kol += 1
            elif i == "6":
                kol += 1
            elif i == "7":
                kol += 1
            elif i == "8":
                kol += 1
            elif i == "9":
                kol += 1
        for i in password:
            if i == "+":
                kol_2 += 1
            elif i == "-":
                kol_2 += 1
            elif i == "=":
                kol_2 += 1
            elif i == "_":
                kol_2 += 1
            elif i == ")":
                kol_2 += 1
            elif i == "(":
                kol_2 += 1
            elif i == "*":
                kol_2 += 1
            elif i == "&":
                kol_2 += 1
            elif i == "^":
                kol_2 += 1
            elif i == "%":
                kol_2 += 1
            elif i == "$":
                kol_2 += 1
            elif i == "#":
                kol_2 += 1
            elif i == "@":
                kol_2 += 1
            elif i == "!":
                kol_2 += 1
            elif i == "?":
                kol_2 += 1
            elif i == ">":
                kol_2 += 1
            elif i == "<":
                kol_2 += 1
        if password.islower() == False and password.isupper() == False:
            if kol >= 1 and kol_2 >= 1:
                addition_users(message.from_user.id, message.from_user.first_name, login_for_registration, password)
                bot.send_message(message.chat.id, "Вы успешно зарегестрированны!")
                start_for_log_in_and_registration(message)
            else:
                bot.send_message(message.chat.id,
                                 'В пароле должна быть хотя бы одна цифра (0123456789) и хотя бы один специальный символ ( +=_-()*?:%;№?>< )')
                start_for_log_in_and_registration(message)
    else:
        bot.send_message(message.chat.id, "Пароль должен состоять минимум из 8 символов!")
        start_for_log_in_and_registration(message)


def random_password_for_registration(message):
    kol = 0
    kol_2 = 0
    global password
    password = ''
    chars = '=+-_)(*&^%$#@?><abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    for n in range(1):
        for i in range(12):
            password += random.choice(chars)
    if password.isupper() == True:
        random_password_for_registration(message)
    if password.islower() == True:
        random_password_for_registration(message)
    for i in password:
        if i == "0":
            kol += 1
        elif i == "1":
            kol += 1
        elif i == "2":
            kol += 1
        elif i == "3":
            kol += 1
        elif i == "4":
            kol += 1
        elif i == "5":
            kol += 1
        elif i == "6":
            kol += 1
        elif i == "7":
            kol += 1
        elif i == "8":
            kol += 1
        elif i == "9":
            kol += 1
    for i in password:
        if i == "+":
            kol_2 += 1
        elif i == "-":
            kol_2 += 1
        elif i == "=":
            kol_2 += 1
        elif i == "_":
            kol_2 += 1
        elif i == ")":
            kol_2 += 1
        elif i == "(":
            kol_2 += 1
        elif i == "*":
            kol_2 += 1
        elif i == "&":
            kol_2 += 1
        elif i == "^":
            kol_2 += 1
        elif i == "%":
            kol_2 += 1
        elif i == "$":
            kol_2 += 1
        elif i == "#":
            kol_2 += 1
        elif i == "@":
            kol_2 += 1
        elif i == "!":
            kol_2 += 1
        elif i == "?":
            kol_2 += 1
        elif i == ">":
            kol_2 += 1
        elif i == "<":
            kol_2 += 1
    if password.islower() == False and password.isupper() == False:
        if kol >= 1 and kol_2 >= 1:
            addition_users(message.from_user.id, message.from_user.first_name, login_for_registration, password)
            bot.send_message(message.chat.id,
                             f"Вы успешно зарегестрированны!\nВаш логин: {login_for_registration}\nВаш пароль: {password}")
            start_for_log_in_and_registration(message)
        else:
            random_password_for_registration(message)


# Отправка по gmail
def the_most_main_start(message):
    markup_5 = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Отправить письмо')
    btn2 = types.KeyboardButton('Отправить массовую рассылку')
    btn3 = types.KeyboardButton('Посмотреть историю отправки писем')
    btn4 = types.KeyboardButton('Выйти из аккаунта')

    markup_5.row(btn1)
    markup_5.row(btn2, btn3)
    markup_5.row(btn4)

    bot.send_message(message.chat.id,
                     f'Вы в главном меню',
                     reply_markup=markup_5)

    bot.register_next_step_handler(message, check_the_most_main_start)


def check_the_most_main_start(message):
    global mass
    if message.text == 'Отправить письмо':
        mass = False
        main_start(message)
    elif message.text == 'Отправить массовую рассылку':
        mass = True
        main_start(message)
    elif message.text == 'Посмотреть историю отправки писем':
        history(message)
    elif message.text == 'Выйти из аккаунта':
        start_for_log_in_and_registration(message)


def main_start(message):
    global mass
    markup_4 = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton('Добавить отправителя/отправителей')
    btn2 = types.KeyboardButton('Добавить заголовок')
    btn3 = types.KeyboardButton('Добавить текст')
    btn4 = types.KeyboardButton('Отправить сообщение')

    markup_4.row(btn1)
    markup_4.row(btn2, btn3)
    markup_4.row(btn4)
    if mass == False:
        bot.send_message(message.chat.id,
                         f'{message.from_user.first_name}, ваше письмо:\nПолучатель: {recipient_1}\nЗаголовок: {article_for_recipient_1}\nТекст сообщения: {message_for_recipient_1}',
                         reply_markup=markup_4)
    else:
        bot.send_message(message.chat.id,
                         f'{message.from_user.first_name}, ваше письмо:\nПолучатели: {"".join(recipient_2)}\nЗаголовок: {article_for_recipient_1}\nТекст сообщения: {message_for_recipient_1}',
                         reply_markup=markup_4)
    bot.register_next_step_handler(message, check_main)


def check_main(message):
    if message.text == "Добавить отправителя/отправителей":
        bot.send_message(message.chat.id,
                         f"{message.from_user.first_name}, введите электронную почту получателя(@gmail.com\@email.ru\@email.com\@yandex.ru):",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, recipient)

    elif message.text == "Добавить заголовок":
        bot.send_message(message.chat.id, "Введите заголовок:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, article_for_recipient)
    elif message.text == "Добавить текст":
        bot.send_message(message.chat.id, "Введите сообщение:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, message_for_recipient)
    elif message.text == "Отправить сообщение":
        send_mail(message)
    else:
        bot.send_message(message.chat.id, "Неизвестная команда!")
        main_start(message)


def recipient(message):
    global recipient_1, mass, recipient_2
    recipient_1 = message.text
    if mass == True:
        recipient_2 += '\n' + str(recipient_1)
    if recipient_1[-10:] == '@gmail.com':
        del_message(message)
        main_start(message)
    elif recipient_1[-9:] == '@email.ru':
        del_message(message)
        main_start(message)
    elif recipient_1[-10:] == '@email.com':
        del_message(message)
        main_start(message)
    elif recipient_1[-10:] == '@yandex.ru':
        del_message(message)
        main_start(message)
    else:
        if mass == False:
            bot.send_message(message.chat.id, 'Вы неправильно ввели электронную почту!\nВозвращаем вас в главное меню!')
            recipient_1 = ''
        else:
            bot.send_message(message.chat.id, 'Вы неправильно ввели электронную почту!\nВозвращаем вас в главное меню!')
            recipient_2.pop(-1)
        time.sleep(2)
        del_message(message)
        main_start(message)


def article_for_recipient(message):
    global article_for_recipient_1
    article_for_recipient_1 = message.text
    del_message(message)
    main_start(message)


def message_for_recipient(message):
    global message_for_recipient_1
    message_for_recipient_1 = message.text
    del_message(message)
    main_start(message)


def send_mail(message):
    global recipient_1, article_for_recipient_1, message_for_recipient_1, mass, recipient_2
    if recipient_1 != '':
        if mass == False:
            sender = 'fedorsmorodskii@gmail.com'
            password = 'ikdnmhifdlzyxgfd'
            poluchatel = str(recipient_1)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            server.login(sender, password)
            msg = MIMEText(str(message_for_recipient_1))
            msg['Subject'] = str(article_for_recipient_1)

            server.sendmail(sender, poluchatel, msg.as_string())
            bot.send_message(message.chat.id, "Сообщение отправленно!")
            addition_information(login, recipient_1, article_for_recipient_1, message_for_recipient_1)
            recipient_1 = ''
            article_for_recipient_1 = ''
            message_for_recipient_1 = ''
            the_most_main_start(message)
        if mass == True:
            kol = 0
            recipient_2 = "".join(recipient_2)
            recipient_2.replace('\n', ' ')
            recipient_2 = recipient_2.split()
            while kol != len(recipient_2):
                sender = 'fedorsmorodskii@gmail.com'
                password = 'ikdnmhifdlzyxgfd'
                poluchatel = str(recipient_2[kol])

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()

                server.login(sender, password)
                msg = MIMEText(str(message_for_recipient_1))
                msg['Subject'] = str(article_for_recipient_1)

                server.sendmail(sender, poluchatel, msg.as_string())
                bot.send_message(message.chat.id, "Сообщение отправленно!")
                addition_information(login, recipient_2[kol], article_for_recipient_1, message_for_recipient_1)
                kol += 1
            recipient_1 = ''
            article_for_recipient_1 = ''
            message_for_recipient_1 = ''
            recipient_2 = []
            the_most_main_start(message)
    else:
        bot.send_message(message.chat.id, 'Введите электронную почту получателя!')
        time.sleep(2)
        del_message(message)
        main_start(message)


def del_message(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.delete_message(message.chat.id, message.message_id - 2)
    bot.delete_message(message.chat.id, message.message_id - 3)


def history(message):
    kol = 0
    cursor.execute("SELECT * FROM information WHERE login = ?", [login])
    b = cursor.fetchall()
    while len(b) != kol:
        a = b[kol]
        bot.send_message(message.chat.id,
                         f'Отправленное письмо:\nПолучатель: {a[2]}\nЗаголовок: {a[3]}\nТекст сообщения: {a[4]}')
        kol += 1
    the_most_main_start(message)


bot.polling(none_stop=True)
