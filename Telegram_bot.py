from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8704404848:AAE2ur5uiJ9zsnCeI99_2-RrrcHz4wDXjLQ"

# 📚 SUBJECT-BASED DATA ONLY
links = {
    "dsa": {
        "Btech Common": "https://www.rtuquestionpapers.com/btech/COMMON/sem-3/data-structures-and-algorithms-3e1652",
        "Btech AI-Data Science": "https://www.rtuquestionpapers.com/btech/ai-data-science/sem-3/data-structures-and-algorithms-3e1202",
        "Btech Bio medical Engineering": "https://www.rtuquestionpapers.com/btech/bio-medical-engineering/sem-3/data-structures-and-algorithms-3e1496",
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # 🔁 SYNONYMS (IMPORTANT)
    if "data structure" in text or "data structures" in text:
        text += " dsa"
    if "operating system" in text:
        text += " os"
    if "database" in text:
        text += " dbms"

    found_subject = None

    # 🔍 FIND SUBJECT DIRECTLY
    for subject in links:
        if subject in text:
            found_subject = subject

    # ✅ IF SUBJECT FOUND → SHOW OPTIONS
    if found_subject:
        subject_data = links[found_subject]

        reply = f"📚 {found_subject.upper()} Papers:\n\n"

        for title, link in subject_data.items():
            reply += f"👉 {title}: {link}\n"

        await update.message.reply_text(reply)

    # ❌ DEFAULT
    else:
        await update.message.reply_text(
            "🤖 I can help you with papers!\n\n"
            "Try typing:\n"
            "👉 DSA\n"
            "👉 Operating System\n"
            "👉 DBMS\n\n"
            "Or visit:\nhttps://rtuquestionpapers.com/"
        )

# 🚀 RUN BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("🤖 Bot is running...")
app.run_polling()
