#!/usr/bin/env python3
from paczkomabot.app import app

if __name__ == '__main__':
    import os
    from paczkomabot.bot import TelegramBot

    TOKEN = os.environ['TOKEN']
    telegram_bot = TelegramBot(TOKEN)

    async def show_webhook_info():
        webhook_info = await telegram_bot.application.bot.get_webhook_info()
        for item in webhook_info.__slots__:
            print(f"{item:24s}: {getattr(webhook_info, item)}")

    import asyncio
    asyncio.run(show_webhook_info())
