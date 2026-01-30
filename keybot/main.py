import os
import random
import string
from telegram import Update
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ===== WEBKEEP ALIVE =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Bot is online!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()
    
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 🔑 Key generator
def generate_key(length=12):
    prefix = "Kaze-"
    chars = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(length))
    return prefix + random_part

# /genkey command
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = generate_key()
    await update.message.reply_text(f"🔑 Generated Key:\n{key}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("genkey", genkey))

    print("🤖 Bot is running using polling...")
    app.run_polling()


if __name__ == "__main__":
    keep_alive()
    main()
