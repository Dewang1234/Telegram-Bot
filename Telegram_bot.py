from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import json
import sys

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ERROR: TOKEN environment variable is not set!")
    sys.exit(1)

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PAPERS_PATH = os.path.join(SCRIPT_DIR, "papers.json")

# Load papers.json with full path
try:
    with open(PAPERS_PATH, "r") as file:
        data = json.load(file)
    print(f"✅ Loaded {len(data)} papers from ABVV University")
except FileNotFoundError:
    print(f"❌ ERROR: papers.json not found at {PAPERS_PATH}")
    data = []
except json.JSONDecodeError:
    print(f"❌ ERROR: papers.json has invalid JSON format!")
    sys.exit(1)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with bot features"""
    welcome_message = f"""
🎓 *Welcome to ABVV University Papers Bot!*

I help you find question papers and study materials for Atal Bihari Vajpayee Vishwavidyalaya (ABVV).

*📌 What I Can Do:*
• Search for question papers by subject name
• Find papers by branch/department
• Get direct download links to papers

*📝 How to Use Me:*
Simply type the *subject name* or *branch name* and I'll find matching papers.

*✅ Examples:*
• `Computer Science`
• `CSE`
• `Mathematics`
• `Physics`

*💡 Tips:*
• Use full subject names for better results
• Try different keywords if no results found
• Type /subjects to see all available subjects

*📚 Total Papers Available:* {len(data)}

Start searching by typing a subject or branch name!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
*❓ How to Use This Bot*

*Search Format:*
Just type the subject name or branch name directly.

*Examples:*
• `Data Science` - Shows Data Science papers
• `CSE` - Shows all Computer Science papers  
• `Mathematics` - Shows Mathematics papers

*What Each Result Shows:*
👉 *Subject Name* (Branch)
🔗 *Download Link*

*No Results?*
• Try using the full subject name
• Check your spelling
• Type /subjects to see what's available

*Commands:*
/start - Show welcome message
/help - Show this help
/subjects - List all available subjects
/branches - List all available branches

*All papers are from ABVV University.*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def subjects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available subjects"""
    subjects = set()
    for item in data:
        subject = item.get("subject_name", "Unknown")
        subjects.add(subject)
    
    subjects_list = sorted(list(subjects))
    
    if subjects_list:
        response = "*📚 Available Subjects in ABVV:*\n\n"
        for subject in subjects_list[:30]:  # Show first 30
            response += f"• {subject}\n"
        
        if len(subjects_list) > 30:
            response += f"\n*+ {len(subjects_list) - 30} more subjects*"
        response += f"\n\n*Total:* {len(subjects_list)} subjects"
    else:
        response = "No subjects found in database."
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def branches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available branches"""
    branches = set()
    for item in data:
        branch = item.get("branch", "Unknown")
        branches.add(branch)
    
    branches_list = sorted(list(branches))
    
    if branches_list:
        response = "*🏫 Available Branches in ABVV:*\n\n"
        for branch in branches_list:
            response += f"• {branch}\n"
        response += f"\n*Total:* {len(branches_list)} branches"
    else:
        response = "No branches found in database."
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search and display papers based on user input"""
    text = update.message.text.lower()
    
    if not data:
        await update.message.reply_text("⚠️ Paper database is empty. Please contact administrator.")
        return
    
    results = []
    
    # SEARCH in JSON
    for item in data:
        subject_name = item.get("subject_name", "").lower()
        branch = item.get("branch", "").lower()
        
        if text in subject_name or text in branch:
            results.append(item)
    
    # IF FOUND
    if results:
        reply = f"🔍 *Found {len(results)} paper(s) in ABVV:*\n\n"
        
        for idx, item in enumerate(results[:10], 1):  # Limit to 10 results
            subject = item.get('subject_name', 'N/A')
            branch = item.get('branch', 'N/A')
            url = item.get('url', '#')
            
            reply += f"*{idx}. {subject}*\n"
            reply += f"   📚 *Branch:* {branch}\n"
            reply += f"   🔗 [Download Link]({url})\n\n"
        
        if len(results) > 10:
            reply += f"\n*Showing first 10 of {len(results)} results.*\n"
            reply += "Try a more specific search term for better results."
        
        await update.message.reply_text(reply, parse_mode='Markdown', disable_web_page_preview=True)
    
    # NOT FOUND
    else:
        not_found_message = """
❌ *No matching papers found in ABVV database.*

*Try these tips:*
• Use the full subject name (e.g., "Data Science" not "DS")
• Check your spelling
• Type /subjects to see all available subjects
• Type /branches to see all available branches

*Example searches:* Data Science, CSE, Mathematics, Physics
        """
        await update.message.reply_text(not_found_message, parse_mode='Markdown')

# START BOT
app = ApplicationBuilder().token(TOKEN).build()

# Add command handlers
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("subjects", subjects_command))
app.add_handler(CommandHandler("branches", branches_command))

# Add message handler for text searches
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🤖 ABVV University Papers Bot is running...")
print(f"📚 Loaded {len(data)} papers from ABVV University")
print("✅ Commands: /start, /help, /subjects, /branches")
app.run_polling()
