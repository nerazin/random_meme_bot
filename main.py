import telebot
import config
import pickledb
import os
from telebot import types

import globals
import imgur_parser
import pasting_a_word

import logging


from telebot import apihelper
apihelper.proxy = {'https':'https://177.87.39.104:3128'}


API_TOKEN = config.TOKEN

bot = telebot.TeleBot(API_TOKEN)



@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_photo = pdb.get('start_photo')
    if start_photo:
        bot.send_photo(message.chat.id, start_photo)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Рандом')

    bot.send_message(message.chat.id, 'Привет. Нажми на кнопку "Рандом", чтобы получить рандомную картинку '
                                      'с рандомным шрифтом и словом\n\nИдея предложена '
                                      'самым модным пупером современности @constixity',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in ['Рандом', '/random'])
def send_random_picture(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    for _ in range(5):
        out_image = imgur_parser.get_image()
        try:
            pasting_a_word.draw_a_word(out_image)
        except OSError:
            os.remove(out_image)
            continue

        with open(out_image, 'rb') as img:
            bot.send_photo(message.chat.id, img)
        os.remove(out_image)
        break
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Пробуй ещё раз. /random')



@bot.message_handler(commands=['cancel'],
                     func=lambda message: message.chat.id == config.ME)
def cancel_everything(message):
    globals.i_must_send_photo_welcome_photo = False
    bot.reply_to(message, 'Отменил')


@bot.message_handler(commands=['set_photo'],
                     func=lambda message: message.chat.id == config.ME)
def setting_welcome_photo(message):
    globals.i_must_send_photo_welcome_photo = True
    bot.reply_to(message, 'Жду')


@bot.message_handler(content_types=['photo'],
                     func=lambda message: message.chat.id == config.ME)
def set_start_photo(message):
    file_id = message.photo[-1].file_id
    if globals.i_must_send_photo_welcome_photo:
        print('Setting up start photo')
        pdb.set('start_photo', file_id)
        bot.reply_to(message, 'Сделано')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, 'Не понял. Извинись. /random')


if __name__ == '__main__':
    print('Working...')

    # logger = telebot.logger
    # telebot.logger.setLevel(logging.DEBUG)

    pdb = pickledb.load('db.pdb', auto_dump=True)
    bot.polling(none_stop=True)
