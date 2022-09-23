import telebot
import sqlite3

from telebot import types

bot = telebot.TeleBot("")

path = 'D:\SQLiteStudio\dogs'


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')


@bot.message_handler(commands=['find'])
def get_name(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='id', callback_data='id')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='name', callback_data='name')
    keyboard.add(key_no)
    key_day = types.InlineKeyboardButton(text='all day', callback_data='all day')
    keyboard.add(key_day)
    key_breed = types.InlineKeyboardButton(text='all breed', callback_data='breed')
    keyboard.add(key_breed)
    question = 'id или имя породы или весь корма для породы или все кормежка за день?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    connection = sqlite3.connect('D:\SQLiteStudio\dogs', check_same_thread=False)
    cursor = connection.cursor()
    if call.data == "id":
        @bot.message_handler(content_types=['text'])
        def get_age(message):
            global id
            id = message.text
            query = f'SELECT * FROM dogs where feedid = {id}'
            row = cursor.execute(query).fetchall()
            bot.send_message(message.chat.id, str(row))

    elif call.data == "name":
        @bot.message_handler(content_types=['text'])
        def get_age(message):
            global name
            name = message.text
            name = f"'{name}'"
            query = f'SELECT * FROM dogs where breedname = {name}'
            row = cursor.execute(query).fetchall()
            bot.send_message(message.chat.id, str(row))
    elif call.data == "all day":
        bot.send_message(call.message.chat.id, 'введите дату в формате YYYY-MM-DD')

        @bot.message_handler(content_types=['text'])
        def get_age(message):
            global day
            day = message.text
            day = f"'{day}'"
            query = f'SELECT * FROM dogs where DATE(feedingtime)= {day}'
            row = cursor.execute(query).fetchall()
            bot.send_message(message.chat.id, str(row))
    elif call.data == "breed":
        @bot.message_handler(content_types=['text'])
        def get_age(message):
            global name
            name = message.text
            name = f"'{name}'"
            query = f'SELECT * FROM (select breedname, sum(feedweight) from dogs group by breedname) as p where p.breedname = {name};'
            row = cursor.execute(query).fetchall()
            bot.send_message(message.chat.id, str(row))


bot.polling(none_stop=True)
