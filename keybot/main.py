import os
import random
import string
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

def generate_key(length=12):
    prefix = "Kaze-"
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(length))

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = generate_key()
    await update.message.reply_text(f"🔑 Generated Key:\n{key}")

telegram_app.add_handler(CommandHandler("genkey", genkey))

@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

@app.post("/webhook")
async def webhook(request: Request):
    update = Update.de_json(await request.json(), telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
