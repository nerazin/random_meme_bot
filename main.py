import telebot
import config
import pickledb
import os
import sys
import logging
from telebot import types
from telebot import apihelper

import cherrypy

import globals
import imgur_parser
import pasting_a_word


bot = telebot.TeleBot(config.TOKEN)


WEBHOOK_HOST = config.HOST_IP
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(config.TOKEN)


def my_logging(message):
    if message.chat.id != config.ME:
        with open('log.log', 'a', encoding='utf-8') as f:
            f.write(str(message.json) + '\n')


# WebhookServer, process webhook calls
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
           'content-type' in cherrypy.request.headers and \
           cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    start_photo = pdb.get('start_photo')
    if start_photo:
        bot.send_photo(message.chat.id, start_photo)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Рандом')

    bot.send_message(message.chat.id, 'Привет. Нажми на кнопку "Рандом", чтобы получить рандомную картинку '
                                      'с рандомным шрифтом и словом.\nУбрать надпись - /help\n\nИдея предложена '
                                      'самым модным пупером современности @constixity',
                     reply_markup=keyboard)
    my_logging(message)


@bot.message_handler(commands=['help'])
def send_help(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Рандом')
    bot.send_message(message.chat.id, 'Жми "Рандом" или /random\n'
                                      'Не добавлять надпись к изображениям - /switch_word_setting',
                     reply_markup=keyboard)


@bot.message_handler(commands=['switch_word_setting'])
def word_setting(message):
    """
    User will be in the list if he don't want that word underneath
    """
    chat_id = message.chat.id

    request = pdb.lgetall(globals.setting_list_name)

    if chat_id in request:
        pdb.lremvalue(globals.setting_list_name, chat_id)
        pdb.dump()
        bot.send_message(chat_id, 'Теперь подпись будет появляться. Изменить - /switch_word_setting')
    else:
        pdb.ladd(globals.setting_list_name, chat_id)
        bot.send_message(chat_id, 'Теперь подписи не будет. Изменить - /switch_word_setting')


@bot.message_handler(func=lambda message: message.text == 'Рандом')
@bot.message_handler(commands=['random'])
def send_random_picture(message):
    # if message.chat.type != "private":
    #     hideBoard = types.ReplyKeyboardRemove()
    #     bot.send_message(message.chat.id, text='Ждём', reply_markup=hideBoard)

    # if message.chat.id in globals.they_want_random:
    #     bot.reply_to(message, 'Подожди. Я ещё отправляю тебе картинку')
    #     return
    # globals.they_want_random.append(message.chat.id)

    bot.send_chat_action(message.chat.id, 'upload_photo')

    db_resp = pdb.lgetall('word_setting')
    if message.chat.id in db_resp:
        # He don't want a word
        out_image = imgur_parser.get_image()
    else:
        for _ in range(5):
            out_image = imgur_parser.get_image()
            try:
                pasting_a_word.draw_a_word(out_image)
            except OSError:
                os.remove(out_image)
                continue
            break
        else:
            bot.send_message(message.chat.id, 'Что-то пошло не так. Пробуй ещё раз. /random')
            return

    with open(out_image, 'rb') as img:
        bot.send_photo(message.chat.id, img)
    os.remove(out_image)

    # globals.they_want_random.remove(message.chat.id)


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


@bot.message_handler(commands=['getlog'],
                     func=lambda message: message.chat.id == config.ME)
def get_log(message):
    bot.send_message(message.chat.id, 'Take Logs')
    with open('log.log', 'rb') as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['photo'],
                     func=lambda message: message.chat.id == config.ME)
def set_start_photo(message):
    file_id = message.photo[-1].file_id
    if globals.i_must_send_photo_welcome_photo:
        print('Setting up start photo')
        pdb.set('start_photo', file_id)
        bot.reply_to(message, 'Сделано')


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True,
                     content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def any_other_message(message):
    if message.chat.type == "private":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Рандом')
        my_logging(message)
        bot.reply_to(message, 'Не понял. Извинись. /random', reply_markup=keyboard)


if __name__ == '__main__':
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

    # Pdb load
    pdb = pickledb.load('db.pdb', auto_dump=True)
    request = pdb.get(globals.setting_list_name)
    if not request:
        pdb.lcreate(globals.setting_list_name)

    print('Working...')

    if len(sys.argv) > 1:
        bot.remove_webhook()

        # Set webhook
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))

        # Disable CherryPy requests log
        access_log = cherrypy.log.access_log
        for handler in tuple(access_log.handlers):
            access_log.removeHandler(handler)

        # Start cherrypy server
        cherrypy.config.update({
            'server.socket_host': WEBHOOK_LISTEN,
            'server.socket_port': WEBHOOK_PORT,
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': WEBHOOK_SSL_CERT,
            'server.ssl_private_key': WEBHOOK_SSL_PRIV
        })

        cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
    else:
        print('To boot with webhook use python3 main.py webhook')
        bot.remove_webhook()
        apihelper.proxy = {'https': 'https://177.87.39.104:3128'}
        bot.polling(none_stop=True)

