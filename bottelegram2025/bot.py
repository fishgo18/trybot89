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
    username = update.message.from_user.username or update.message.from_user.full_name
    now = datetime.datetime.now()

    user_status[user_id] = {
        "status": "keluar",
        "time": now,
        "username": username
    }

    await update.message.reply_text("✅ Timer keluar dimulai. Anda punya 15 menit untuk kembali.")

    def check_back():
        if user_status.get(user_id, {}).get("status") == "keluar":
            context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Anda belum kembali dalam 15 menit!"
            )
            # Bisa ditambahkan: kirim ke grup HR/log
            print(f"[ALERT] {username} belum kembali sejak {now.strftime('%H:%M:%S')}")

    scheduler.add_job(check_back, trigger='date', run_date=now + datetime.timedelta(minutes=15))

async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_status[user_id] = {
        "status": "kembali",
        "time": datetime.datetime.now()
    }
    await update.message.reply_text("✅ Selamat datang kembali!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("kembali", kembali))

app.run_polling()
