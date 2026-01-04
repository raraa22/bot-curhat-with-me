# bot.py
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from groq import Groq

# === Ambil environment variables ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN tidak ditemukan di environment")

# Groq otomatis membaca GROQ_API_KEY dari environment
client = Groq()

# Riwayat chat per user
user_history = {}

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /start"""
    await update.message.reply_text(
        "Halo! Bot AI sudah aktif 🤖\nSilakan tanya apa saja."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan user"""
    user_id = update.effective_user.id
    user_text = update.message.text

    # Simpan riwayat user
    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append({"role": "user", "content": user_text})

    try:
        # Kirim ke Groq LLM
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah teman ngobrol yang suportif dan tidak menghakimi. "
                        "Kamu bukan pengganti profesional. "
                        "Jika user terlihat tertekan, sarankan bicara ke orang terpercaya."
                    )
                }
            ] + user_history[user_id][-6:]  # ambil 6 pesan terakhir
        )

        # Ambil jawaban AI
        reply = response.choices[0].message.content
        user_history[user_id].append({"role": "assistant", "content": reply})

        # Kirim ke user
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("❌ Terjadi error saat memproses AI.")
        print("Error Groq:", e)

# === Main ===
def main():
    # Buat application modern (PTB v20+)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Daftarkan handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot sedang berjalan...")
    # Jalankan bot
    app.run_polling()

if __name__ == "__main__":
    main()
