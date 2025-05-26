import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TELEGRAM_TOKEN or not TOGETHER_API_KEY:
    raise ValueError("TELEGRAM_TOKEN یا TOGETHER_API_KEY تعریف نشده است.")

# حافظه گفتگو کاربران
user_sessions = {}

# پیام متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text
    logging.info(f"User {user_id}: {user_input}")

    if user_id not in user_sessions:
        user_sessions[user_id] = []

    user_sessions[user_id].append({"role": "user", "content": user_input})

    try:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": user_sessions[user_id],
            "max_tokens": 500,
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()
        logging.info(f"Together raw response: {result}")

        if "choices" not in result:
            raise ValueError(f"Unexpected response from Together API: {result}")

        reply = result["choices"][0]["message"]["content"]
        user_sessions[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)

        # ذخیره در فایل
        with open("log.txt", "a") as f:
            f.write(f"User {user_id}: {user_input}\nBot: {reply}\n\n")

    except Exception as e:
        logging.error(f"Together API error: {e}")
        await update.message.reply_text("خطا در ارتباط با مدل زبان.")

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من یک بات هوش مصنوعی هستم. فقط پیام بده :)")

# دستور help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سؤالت رو تایپ کن تا با مدل زبانی پاسخ بدم.")

# منو
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("راهنما", callback_data='help')],
        [InlineKeyboardButton("شروع", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_markup)

# واکنش به دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await query.edit_message_text("این بخش راهنمایی است.")
    elif query.data == 'start':
        await query.edit_message_text("شروع شد!")

# خطای عمومی
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Unhandled exception:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("خطای داخلی بات.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logging.info("Bot is running...")
    app.run_polling()
