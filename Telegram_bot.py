from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import json

TOKEN = os.getenv("TOKEN")

with open("papers.json", "r") as file:
    data = json.load(file)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    results = []

    # SEARCH in JSON
    for item in data:
        if text in item["subject_name"].lower() or text in item["branch"].lower():
            results.append(item)

    # IF FOUND
    if results:
        reply = "📚 Matching Papers:\n\n"

        for item in results[:5]:  # limit results
            reply += f"👉 {item['subject_name']}\n"
            reply += f"🔗 {item['url']}\n\n"

        await update.message.reply_text(reply)

    # NOT FOUND
    else:
        await update.message.reply_text("❌ No matching papers found.")

# START BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()
