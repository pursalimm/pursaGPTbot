from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai
import os

TELEGRAM_TOKEN = os.getenv("7870376967:AAH0uLlL-OcP-9uu-x71wrJ5eBqHWhQHC_s")
OPENAI_API_KEY = os.getenv("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")

openai.api_key = OPENAI_API_KEY

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}]
    )

    reply = response['choices'][0]['message']['content']
    await update.message.reply_text(reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
