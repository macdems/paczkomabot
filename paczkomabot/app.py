import os

from quart import Quart, request

from .bot import TelegramBot
from .qr import qrcode_inpost, qrcode_dhl, qrcode_allegro

TOKEN = os.environ['TOKEN']
telegram_bot = TelegramBot(TOKEN)

app = Quart(__name__)


@app.route('/' + TOKEN, methods=['GET', 'POST'])
async def webhook():
    #json = await request.get_json(force=True)
    json = await request.get_json()
    if json:
        await telegram_bot.process(json)
    return 'OK'


@app.route('/')
async def root():
    return 'OK'


@app.route('/qr/<company>/<phone>/<code>')
async def qr(company, phone, code):
    if company == 'inpost':
        img = qrcode_inpost(phone, code)
    elif company == 'dhl':
        img = qrcode_dhl(phone, code)
    elif company == 'allegro':
        img = qrcode_allegro(phone, code)
    else:
        return 'Not found', 404
    return img.read(), 200, {'Content-Type': 'image/jpeg'}


@app.route('/setwebhook')
async def set_webhook():
    domain = request.host
    url = await telegram_bot.set_webhook(domain)
    return f'Webhook set to: <code>{url}/&lt;token&gt;</code>'
