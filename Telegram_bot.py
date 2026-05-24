from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import json
import sys

TOKEN = os.getenv("TOKEN")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPERS_PATH = os.path.join(SCRIPT_DIR, "papers.json")

# Load papers.json with full path
try:
    with open(PAPERS_PATH, "r") as file:
        data = json.load(file)
    print(f"✅ Loaded papers.json from {PAPERS_PATH}")
except FileNotFoundError:
    print(f"❌ ERROR: papers.json not found at {PAPERS_PATH}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    sys.exit(1)

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
