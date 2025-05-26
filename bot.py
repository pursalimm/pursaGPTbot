import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

# تنظیم لاگر
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# دریافت کلیدها از متغیرهای محیطی
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TELEGRAM_TOKEN or not TOGETHER_API_KEY:
    raise ValueError("TELEGRAM_TOKEN یا TOGETHER_API_KEY تعریف نشده است.")

# هندلر پیام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logging.info(f"User: {user_input}")

    try:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": user_input}],
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
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Together API error: {e}")
        await update.message.reply_text("خطا در ارتباط با مدل زبان.")

# هندلر خطا
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Unhandled exception:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("خطای داخلی بات.")

# اجرای برنامه
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    logging.info("Bot is running...")
    app.run_polling()
