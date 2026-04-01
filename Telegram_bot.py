from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import json

# 🔐 Use environment variable (IMPORTANT for Render)
TOKEN = os.getenv("TOKEN")

with open("papers.json", "r") as file:
    links = json.load(file)
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # synonyms
    if "data structure" in text:
        text += " dsa"

    found_subject = None

    for subject in links:
        if subject in text:
            found_subject = subject
            break

    if found_subject:
        reply = f"📚 {found_subject.upper()} Papers:\n\n"

        for title, link in links[found_subject].items():
            reply += f"👉 {title}:\n{link}\n\n"

        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("❌ No data found")

# 🚀 START BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()
