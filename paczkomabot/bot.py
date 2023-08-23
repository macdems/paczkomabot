import re
from uuid import uuid4

from telegram import Update, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler
from telegram.ext.filters import Regex

from .qr import make_qr_code_image

MESSAGE_RE = re.compile(r'.*kod(?:em)? (?P<code>\d+) .*numer telefonu (?P<phone>\d{9}).*')
NUMBERS_RE = re.compile(r'(?P<phone>\d{9})\s+(?P<code>\d+)')


class TelegramBot:

    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).updater(None).build()

        self.application.add_handler(MessageHandler(Regex(MESSAGE_RE), self.process_message))
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(InlineQueryHandler(self.inline_query))

    async def process(self, json):
        update = Update.de_json(json, self.application.bot)
        await self.application.process_update(update)

    async def set_webhook(self, domain):
        await self.application.bot.set_webhook(url=f'https://{domain}/{self.token}')
        return await self.get_webhook_url_base()

    async def get_webhook_url_base(self):
        webhook_info = await self.application.bot.get_webhook_info()
        return webhook_info.url.rsplit('/', 1)[0]

    async def process_message(self, update, context):
        phone, code = context.matches[0].group('phone', 'code')
        img = make_qr_code_image(phone, code)
        await update.message.reply_photo(img)

    async def start(self, update, context):
        await update.message.reply_text(
            "Udostępnij mi powiadomienie o przyjściu paczki z aplikacji InPost, a ja wygeneruję kod QR."
        )

    async def inline_query(self, update, context):
        query = update.inline_query.query
        m = NUMBERS_RE.match(query) or MESSAGE_RE.match(query)
        if not m: return

        phone, code = m.group('phone', 'code')

        url = f'{await self.get_webhook_url_base()}/qr/{phone}/{code}'
        results = [
            InlineQueryResultPhoto(
                id=uuid4(),
                title="Kod QR",
                caption=f"Paczka na numer telefonu {phone} z kodem odbioru {code}",
                photo_url=url,
                thumb_url=f'{url}?thumb=true',
                photo_width=310,
                photo_height=310
            )
        ]

        await update.inline_query.answer(results)
