import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

user_status = {}
scheduler = BackgroundScheduler()
scheduler.start()

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Gunakan /keluar saat Anda keluar, dan /kembali saat kembali.")

async def keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_status[user_id] = False
    await update.message.reply_text("Timer keluar dimulai. Anda punya 15 menit untuk kembali.")

    def check_back():
        if not user_status.get(user_id, True):
            context.bot.send_message(chat_id=user_id, text="⚠️ Anda belum kembali dalam 15 menit!")

    scheduler.add_job(check_back, trigger='date', run_date=None, seconds=15*60)

async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_status[user_id] = True
    await update.message.reply_text("Selamat datang kembali!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("kembali", kembali))

app.run_polling()