from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

# 🔐 Use environment variable (IMPORTANT for Render)
TOKEN = os.getenv("TOKEN")

# 📚 SUBJECT-BASED DATA
links = {
    "dsa": {
        "Btech Common": "https://www.rtuquestionpapers.com/btech/COMMON/sem-3/data-structures-and-algorithms-3e1652",
        "Btech AI-Data Science": "https://www.rtuquestionpapers.com/btech/ai-data-science/sem-3/data-structures-and-algorithms-3e1202",
        "Btech Bio Medical Engineering": "https://www.rtuquestionpapers.com/btech/bio-medical-engineering/sem-3/data-structures-and-algorithms-3e1496",
        "Btech Computer Science": "https://www.rtuquestionpapers.com/btech/computer-science/sem-3/data-structures-and-algorithms-3e1202"
    },
    "os": {
        "Unit 1": "https://rtuquestionpapers.com/os/unit1",
        "Unit 2": "https://rtuquestionpapers.com/os/unit2"
    },
    "dbms": {
        "Unit 1": "https://rtuquestionpapers.com/dbms/unit1",
        "Unit 2": "https://rtuquestionpapers.com/dbms/unit2"
    }
}

# 🤖 HANDLE MESSAGE
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # 🔁 SYNONYMS (BETTER COVERAGE)
    if "data structure" in text or "data structures" in text:
        text += " dsa"
    if "dsa" in text:
        text += " dsa"
    if "operating system" in text or "os" in text:
        text += " os"
    if "database" in text or "dbms" in text:
        text += " dbms"

    found_subject = None

    # 🔍 FIND SUBJECT (STOP AFTER FIRST MATCH)
    for subject in links:
        if subject in text:
            found_subject = subject
            break

    # ✅ SUBJECT FOUND → SHOW OPTIONS
    if found_subject:
        subject_data = links[found_subject]

        reply = f"📚 {found_subject.upper()} Papers:\n\n"

        for title, link in subject_data.items():
            reply += f"👉 {title}:\n{link}\n\n"

        await update.message.reply_text(reply)

    # ❌ DEFAULT RESPONSE
    else:
        await update.message.reply_text(
            "🤖 I can help you find papers!\n\n"
            "Try typing:\n"
            "👉 DSA\n"
            "👉 Operating System\n"
            "👉 DBMS\n\n"
            "Or visit:\nhttps://rtuquestionpapers.com/"
        )

# 🚀 START BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 Bot is running...")
app.run_polling()
