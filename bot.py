import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

WELCOME_MESSAGE = """👋 Welcome, {name}!

🎓 Welcome to our group.

📌 Please read the pinned message first.
📚 Notes and important updates will be shared here.
❓ If you have a question, feel free to ask.

Enjoy learning ❤️
"""

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        name = member.first_name or "there"
        await update.message.reply_text(
            WELCOME_MESSAGE.format(name=name)
        )

async def health(request):
    return web.Response(text="Telegram welcome bot is running.")

async def run_health_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Set it in Render environment variables.")

    telegram_app = Application.builder().token(BOT_TOKEN).build()
    telegram_app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
    )

    await run_health_server()

    print("✅ Welcome bot is running...")
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
