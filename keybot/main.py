import os
import random
import string
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from threading import Thread
from flask import Flask

# ===== KEEP ALIVE (OPTIONAL) =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Bot is online!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(
        target=lambda: app_web.run(host="0.0.0.0", port=port),
        daemon=True
    ).start()

# ===== CONFIG =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PH_TZ = ZoneInfo("Asia/Manila")

# ===== IN-MEMORY KEY STORAGE =====
keys_db = {}

# ===== KEY GENERATOR =====
def generate_key(length=12):
    prefix = "Kaze-"
    chars = string.ascii_letters + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(length))

# ===== TIME PARSER =====
def parse_duration(text: str):
    try:
        value = int(text[:-1])
        unit = text[-1].lower()

        if unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)
    except:
        pass
    return None

# ===== /genkey =====
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/genkey 1m\n/genkey 1h\n/genkey 1d"
        )
        return

    duration = parse_duration(context.args[0])
    if not duration:
        await update.message.reply_text("❌ Invalid format. Use 1m, 1h, or 1d")
        return

    key = generate_key()
    expire_time = datetime.now(PH_TZ) + duration
    keys_db[key] = expire_time

    await update.message.reply_text(
        f"🔑 Generated Key:\n{key}\n\n"
        f"⏰ Expires (PH): {expire_time.strftime('%Y-%m-%d %I:%M %p')}"
    )

# ===== /checkkey =====
async def checkkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /checkkey YOUR_KEY")
        return

    key = context.args[0]
    expire_time = keys_db.get(key)

    if not expire_time:
        await update.message.reply_text("❌ Invalid key")
        return

    if datetime.now(PH_TZ) > expire_time:
        del keys_db[key]
        await update.message.reply_text(
            "❌ Key expired you need to genkey again"
        )
        return

    await update.message.reply_text("✅ Key is still valid")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("checkkey", checkkey))

    print("🤖 Bot is running using polling...")
    app.run_polling()

if __name__ == "__main__":
    keep_alive()  # optional
    main()
