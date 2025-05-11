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
scheduler = AsyncIOScheduler()
scheduler.start()

# 🔑 Token dari environment variable
TOKEN = os.getenv("BOT_TOKEN")

# 🚀 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Gunakan /keluar saat Anda keluar, dan /kembali saat kembali."
    )

# 🟡 /keluar command
async def keluar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user = update.message.from_user
    now = datetime.datetime.now()

    username = user.username or f"{user.first_name} {user.last_name or ''}".strip()

    # Status awal
    user_status[user_id] = {
        "status": "keluar",
        "start_time": now,
        "username": username,
        "message_id": None
    }

    # Kirim pesan awal
    sent_msg = await update.message.reply_text("⏳ Timer keluar dimulai.\nWaktu tersisa: 15 menit.")
    user_status[user_id]["message_id"] = sent_msg.message_id

    # Schedule countdown per menit
    for i in range(1, 16):  # 1 sampai 15 menit
        scheduler.add_job(
            countdown_update,
            trigger='date',
            run_date=now + datetime.timedelta(minutes=i),
            args=[context, chat_id, user_id, 15 - i]
        )

    # Schedule alert akhir
    scheduler.add_job(
        alert_expired,
        trigger='date',
        run_date=now + datetime.timedelta(minutes=15),
        args=[context, chat_id, user_id]
    )

# Fungsi update countdown
async def countdown_update(context, chat_id, user_id, minutes_left):
    status = user_status.get(user_id, {})
    if status.get("status") != "keluar":
        return  # Sudah kembali, stop edit

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status["message_id"],
            text=f"⏳ Timer keluar aktif.\nWaktu tersisa: {minutes_left} menit."
        )
    except Exception as e:
        logging.error(f"Gagal update countdown: {e}")

# Fungsi alert jika tidak kembali
async def alert_expired(context, chat_id, user_id):
    status = user_status.get(user_id, {})
    if status.get("status") == "keluar":
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Anda belum kembali dalam 15 menit!"
        )
        logging.warning(f"[ALERT] {status.get('username')} belum kembali setelah 15 menit.")

# 🟢 /kembali command
async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_status:
        user_status[user_id]["status"] = "kembali"
    await update.message.reply_text("✅ Selamat datang kembali!")

# Setup bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("keluar", keluar))
app.add_handler(CommandHandler("kembali", kembali))

# Jalankan bot
app.run_polling()
