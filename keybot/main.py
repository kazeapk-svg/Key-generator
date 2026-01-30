import os
import random
import string
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)
from threading import Thread
from flask import Flask

# ===== KEEP ALIVE =====
app_web = Flask(__name__)

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
OWNER_ID = 123456789  # 🔥 PALITAN MO
PH_TZ = ZoneInfo("Asia/Manila")

# ===== STORAGE =====
keys_db = {}

# ===== KEY GENERATOR =====
def generate_key(length=12):
    return "Kaze-" + ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )

# ===== TIME PARSER =====
def parse_duration(text):
    try:
        v = int(text[:-1])
        u = text[-1].lower()
        if u == "m": return timedelta(minutes=v)
        if u == "h": return timedelta(hours=v)
        if u == "d": return timedelta(days=v)
    except:
        pass
    return None

# ===== INLINE KEYBOARD =====
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Generate ACCESS Key", callback_data="access_menu")],
        [InlineKeyboardButton("🔑 Generate RANDOM Key", callback_data="random_key")],
        [InlineKeyboardButton("🗑 Revoke ACCESS Key", callback_data="revoke_info")]
    ])

def access_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("1 Minute", callback_data="access_1m"),
            InlineKeyboardButton("1 Hour", callback_data="access_1h")
        ],
        [InlineKeyboardButton("1 Day", callback_data="access_1d")]
    ])

# ===== AUTO EXPIRE =====
async def expire_key_after(duration, key, chat_id, app):
    await asyncio.sleep(duration.total_seconds())
    if key in keys_db:
        del keys_db[key]
        await app.bot.send_message(
            chat_id,
            f"❌ ACCESS KEY EXPIRED\n\n📝 `{key}`",
            parse_mode="Markdown"
        )

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Owner only panel")
        return

    await update.message.reply_text(
        "⚙️ OWNER CONTROL PANEL",
        reply_markup=start_keyboard()
    )

# ===== INLINE HANDLER =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.from_user.id != OWNER_ID:
        await q.message.reply_text("❌ Owner only")
        return

    if q.data == "access_menu":
        await q.message.reply_text(
            "Select ACCESS KEY duration:",
            reply_markup=access_keyboard()
        )
        return

    if q.data.startswith("access_"):
        duration = parse_duration(q.data.replace("access_", ""))
        key = generate_key()
        expire = datetime.now(PH_TZ) + duration
        keys_db[key] = expire

        await q.message.reply_text(
            f"🔐 ACCESS KEY GENERATED\n\n"
            f"🔑 `{key}`\n"
            f"📅 Expires:\n{expire.strftime('%B %d, %Y • %I:%M %p')}",
            parse_mode="Markdown"
        )

        asyncio.create_task(
            expire_key_after(duration, key, q.message.chat_id, context.application)
        )
        return

    if q.data == "random_key":
        key = generate_key()
        await q.message.reply_text(
            f"🔑 RANDOM KEY:\n`{key}`\n\n⚠️ Not valid for access",
            parse_mode="Markdown"
        )
        return

    if q.data == "revoke_info":
        await q.message.reply_text(
            "🗑 Revoke access key using:\n/revoke YOUR_KEY",
            parse_mode="Markdown"
        )

# ===== /genkey (COMMAND STILL WORKS) =====
async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = generate_key()
    await update.message.reply_text(f"🔑 Random Key:\n`{key}`", parse_mode="Markdown")

# ===== /revoke =====
async def revoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Owner only")
        return

    if not context.args:
        await update.message.reply_text("Usage: /revoke KEY")
        return

    key = context.args[0]
    if key in keys_db:
        del keys_db[key]
        await update.message.reply_text("🗑 Access key revoked")
    else:
        await update.message.reply_text("❌ Key not found")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genkey", genkey))
    app.add_handler(CommandHandler("revoke", revoke))
    app.add_handler(CallbackQueryHandler(buttons))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    keep_alive()
    main()
