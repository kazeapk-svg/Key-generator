import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== WEBKEEP ALIVE =====
app_web = Flask(__name__)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

@app_web.route("/")
def home():
    return "Bot is online!"

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    Thread(target=lambda: app_web.run(host="0.0.0.0", port=port)).start()
  
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin IDs (kayong dalawa lang)
ADMIN_IDS = [
    7201369115,   # ID mo
    7764718773    # ID ng kasama mo
]

STARTED_USERS = set()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    STARTED_USERS.add(user.id)

    welcome_message = (
        f"Hello {user.first_name}, 👋\n\n"
        "Thank you for contacting us and welcome! 🎉\n\n"
        "Are you interested in purchasing the **FULL FEATURES MLBB Mod Menu**? 💎\n"
        "This premium version offers a more **advanced**, **stable**, and **secure** "
        "experience compared to the free version 🚀\n\n"
        "📩 To continue, please send **any message**.\n"
        "Once you send a message, the **owner/admins will be notified immediately** "
        "and will assist you as soon as possible ⚡\n\n"
        "Thank you for your interest and support! 🔥"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")


# Forward buyer message to admins
async def forward_to_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    if user.id not in STARTED_USERS:
        await update.message.reply_text("⚠️ Please type /start first.")
        return

    text = update.message.text

    admin_msg = (
        "📩 NEW BUYER MESSAGE\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name: {user.full_name}\n"
        f"🆔 User ID: {user.id}\n"
        f"💬 Message:\n{text}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(admin_id, admin_msg)

    await update.message.reply_text(
        "Thank you for your message! 🙏\n\n"
        "Please wait for our reply, or you may **DM the Owner/Admins immediately** "
        "for faster assistance ⚡\n\n"
        "📩 **DM Contacts:**\n"
        "• @KAZEHAYAMODZ\n"
        "• @phia_maganda\n\n"
        "We appreciate your patience and support! 💎🔥",
        parse_mode="Markdown"
    )


# /user <user_id> <message>  (ADMIN REPLY)
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.message.from_user

    # Security: admins only
    if sender.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage:\n/user <user_id> <message>"
        )
        return

    target_user_id = int(context.args[0])
    reply_text = " ".join(context.args[1:])

    admin_username = f"@{sender.username}" if sender.username else sender.full_name

    final_message = (
        f"💬 Message from {admin_username}:\n"
        f"{reply_text}"
    )

    try:
        await context.bot.send_message(
            chat_id=target_user_id,
            text=final_message
        )
        await update.message.reply_text("✅ Message sent to buyer successfully.")
    except Exception as e:
        await update.message.reply_text("❌ Failed to send message. User may have blocked the bot.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("user", reply_to_user))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admins)
    )

    app.run_polling()


if __name__ == "__main__":
    keep_alive()
    main()
