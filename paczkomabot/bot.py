import re
from uuid import uuid4

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler
from telegram.ext.filters import Regex

from .qr import qrcode_inpost, qrcode_dhl

INPOST_MESSAGE_RE = re.compile(r'.*kod(?:em)? (?P<code>\d+) .*numer telefonu (?P<phone>\d{9}).*')
DHL_MESSAGE_RE = re.compile(r'Paczka (?P<parcel>\d+), PIN (?P<pin>\d{6})\..*DHL BOX.*')

INPOST_NUMBERS_RE = re.compile(r'P\|(?P<phone>\d{9})\|(?P<code>\d+)')
DHL_NUMBERS_RE = re.compile(r'(?P<pin>\d{6})\|(?P<parcel>\d+)')


class TelegramBot:

    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).updater(None).build()

        self.application.add_handler(MessageHandler(Regex(INPOST_MESSAGE_RE), self.process_inpost_message))
        self.application.add_handler(MessageHandler(Regex(DHL_MESSAGE_RE), self.process_dhl_message))
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(InlineQueryHandler(self.inline_query))

    async def process(self, json):
        update = Update.de_json(json, self.application.bot)
        if not self.application._initialized:
            await self.application.initialize()
        await self.application.process_update(update)

    async def set_webhook(self, domain):
        await self.application.bot.set_webhook(url=f'https://{domain}/{self.token}')
        return await self.get_webhook_url_base()

    async def get_webhook_url_base(self):
        webhook_info = await self.application.bot.get_webhook_info()
        return webhook_info.url.rsplit('/', 1)[0]

    async def process_inpost_message(self, update, context):
        phone, code = context.matches[0].group('phone', 'code')
        img = qrcode_inpost(phone, code)
        await update.message.reply_photo(img)

    async def process_dhl_message(self, update, context):
        parcel, pin = context.matches[0].group('parcel', 'pin')
        img = qrcode_dhl(parcel, pin)
        await update.message.reply_photo(img)

    async def start(self, update, context):
        await update.message.reply_text(
            "Udostępnij mi powiadomienie o przyjściu paczki z aplikacji InPost lub SMSa o przesyłce DHL BOX, a ja wygeneruję kod QR."
        )

    async def inline_query(self, update, context):
        query = update.inline_query.query

        if match_inpost := (INPOST_MESSAGE_RE.match(query) or INPOST_NUMBERS_RE.match(query)):
            phone, code = match_inpost.group('phone', 'code')
            url = f'{await self.get_webhook_url_base()}/qr/inpost/{phone}/{code}'
            caption = f"Paczka na numer telefonu {phone} z kodem odbioru {code}"
        elif match_dhl := (DHL_MESSAGE_RE.match(query) or DHL_NUMBERS_RE.match(query)):
            parcel, pin = match_dhl.group('parcel', 'pin')
            url = f'{await self.get_webhook_url_base()}/qr/dhl/{parcel}/{pin}'
            caption = f"Przesyłka w DHL BOX o numerze {parcel}, PIN {pin}"
        else:
            return

        results = [
            InlineQueryResultPhoto(
                id=uuid4(), title="Kod QR", caption=caption, photo_url=url, thumb_url=url, photo_width=310, photo_height=310
            )
        ]

        await update.inline_query.answer(results)
