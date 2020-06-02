import telebot
import config
import random
import utils
from SQLighter import SQLighter
from telebot import types

bot = telebot.TeleBot(config.token)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton(text='/game'))

@bot.message_handler(commands=['start'])
def starting(message):
    bot.send_message(message.chat.id, reply_markup=keyboard, text='Нажми на кнопку и приступим')

@bot.message_handler(commands=['game'])
def game(message):
    db_worker = SQLighter(config.database_name)
    row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    markup = utils.generate_markup(row[2], row[3])
    bot.send_message(message.chat.id, row[1], reply_markup=markup)
    utils.set_user_game(message.chat.id, row[2])
    db_worker.close()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    answer = utils.get_answer_for_user(message.chat.id)
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game',
                         reply_markup=keyboard)
    else:
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не правы. '
                                              'Попробуйте ещё раз!', reply_markup=keyboard)
        utils.finish_user_game(message.chat.id)


if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    bot.infinity_polling()