import os

from quart import Quart, request

from .bot import TelegramBot
from .qr import make_qr_code_image

TOKEN = os.environ['TOKEN']
telegram_bot = TelegramBot(TOKEN)

app = Quart(__name__)


@app.before_serving
async def initialize():
    await telegram_bot.application.initialize()


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


@app.route('/qr/<phone>/<code>')
async def qr(phone, code):
    thumb = request.args.get('thumb', False)
    img = make_qr_code_image(phone, code, thumb)[0]
    return img.read(), 200, {'Content-Type': 'image/jpeg'}


@app.route('/setwebhook')
async def set_webhook():
    domain = request.host
    url = await telegram_bot.set_webhook(domain)
    return f'Webhook set to: <code>{url}/&lt;token&gt;</code>'
