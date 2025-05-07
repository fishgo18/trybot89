import os
import datetime
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 🔧 Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🌐 Simpan status user
user_status = {}

# 🗓 Scheduler berbasis asyncio (bukan thread)
scheduler = AsyncIOScheduler()
scheduler.start()

# 🔑 Token dari environment (gunakan .env di Railway atau Replit)
TOKEN = os.getenv("BOT_TOKEN")

# 🚀 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Gunakan /keluar saat Anda keluar, dan /kembali saat kembali."
    )

# 🟡 /keluar command
async def keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user = update.message.from_user
    now = datetime.datetime.now()

    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()

    user_status[user_id] = {
        "status": "keluar",
        "time": now,
        "username": username
    }

    await update.message.reply_text("✅ Timer keluar dimulai. Anda punya 15 menit untuk kembali.")

    # ✅ Fungsi async untuk pengecekan
    async def check_back():
        if user_status.get(user_id, {}).get("status") == "keluar":
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ Anda belum kembali dalam 15 menit!"
            )
            logging.warning(f"[ALERT] {username} belum kembali sejak {now.strftime('%H:%M:%S')}")

    # ⏱ Jadwalkan 15 menit ke depan
    scheduler.add_job(
        check_back,
        trigger='date',
        run_date=now + datetime.timedelta(minutes=15)
    )

# 🟢 /kembali command
async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_status[user_id] = {
        "status": "kembali",
        "time": datetime.datetime.now()
    }
    await update.message.reply_text("✅ Selamat datang kembali!")

# 🛠 Setup & handler
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("kembali", kembali))

# ▶️ Jalankan polling
app.run_polling()
