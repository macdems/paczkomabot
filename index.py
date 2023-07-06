#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import qrcode

from io import BytesIO

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

from flask import Flask, request


TOKEN = os.environ['TOKEN']


class TelegramBot(object):

    def __init__(self, token):
        self.bot = Bot(token)
        self.token = token
        self.dispatcher = Dispatcher(self.bot, None, workers=0, use_context=True)
        self.add_handlers()

    def set_webhook(self):
        self.bot.set_webhook(
            url='https://inpostqrbot.vercel.app/{}'.format(self.token),
        )

    def make_qr_code(self, update, context):
        match = context.matches[0]
        data = match.groups()
        #update.message.reply_text("http://paczkomaty.pl/{1}/code/{0}".format(*match.groups()))
        qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
        qr.add_data('P|{1}|{0}'.format(*data))
        img = BytesIO()
        img.name = 'inpost-{1}-{0}.jpg'.format(*data)
        qr.make_image().save(img, 'JPEG')
        img.seek(0)
        update.message.reply_photo(img)

    def start(self, update, context):
        update.message.reply_text("Udostępnij mi powiadomienie o przyjściu paczki z aplikacji InPost, a ja wygeneruję kod QR.")

    def add_handlers(self):
        self.dispatcher.add_handler(MessageHandler(Filters.regex('.*kod(?:em)? (\d+) .*numer telefonu (\d+).*'), self.make_qr_code))
        self.dispatcher.add_handler(CommandHandler("start", self.start))

    def process(self, json):
        update = Update.de_json(json, self.bot)
        self.dispatcher.process_update(update)


telegram_bot = TelegramBot(TOKEN)


## Flask part ##

app = Flask(__name__)


@app.route('/'+TOKEN, methods=['GET', 'POST'])
def webhook():
    #json = request.get_json(force=True)
    json = request.get_json()
    if json:
        telegram_bot.process(json)
    return 'OK'


@app.route('/')
def ok():
    telegram_bot.set_webhook()
    return 'OK'


if __name__ == '__main__':
    for item in telegram_bot.bot.get_webhook_info().__dict__.items():
        print("{:24s}: {}".format(*item))
