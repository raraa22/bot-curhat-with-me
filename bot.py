from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
from groq import Groq

# === Ambil ENV ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN tidak ditemukan di environment")

# Groq otomatis baca GROQ_API_KEY dari environment
client = Groq()

# Simpan riwayat chat user
user_history = {}

# Handler start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Bot AI sudah aktif 🤖\nSilakan tanya apa saja."
    )

# Handler pesan
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah teman ngobrol yang suportif dan tidak menghakimi. "
                        "Kamu bukan pengganti profesional. Jika user terlihat sangat tertekan, "
                        "sarankan bicara ke orang terpercaya."
                    )
                }
            ] + user_history[user_id][-6:]
        )

        reply = response.choices[0].message.content
        user_history[user_id].append({"role": "assistant", "content": reply})

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("❌ Terjadi error saat memproses AI.")
        print(e)

# Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot sedang berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
