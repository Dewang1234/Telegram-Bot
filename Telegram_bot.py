from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import os
import json
import sys
import math

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

# Store user search results temporarily
user_sessions = {}

# Constants for pagination
ITEMS_PER_PAGE = 10

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with bot features"""
    total_subjects = len(set(item.get("subject_name", "") for item in data))
    
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
• Use /subjects to browse all {total_subjects} subjects
• Use /branches to see available branches

*📚 Total Papers:* {len(data)}
*📖 Total Subjects:* {total_subjects}

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

*Navigation:*
• Use *Next* and *Previous* buttons to browse through results
• Type /subjects to browse all available subjects
• Type /branches to see all available branches

*Commands:*
/start - Show welcome message
/help - Show this help
/subjects - Browse all subjects (with pagination)
/branches - List all available branches

*All papers are from ABVV University.*
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def subjects_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available subjects with pagination"""
    # Get unique subjects
    subjects = sorted(list(set(item.get("subject_name", "Unknown") for item in data)))
    total_subjects = len(subjects)
    
    if not subjects:
        await update.message.reply_text("No subjects found in database.")
        return
    
    # Store in user session
    user_id = update.effective_user.id
    user_sessions[user_id] = {
        'type': 'subjects',
        'data': subjects,
        'total': total_subjects
    }
    
    # Show first page
    await show_subjects_page(update, user_id, 0)

async def show_subjects_page(update: Update, user_id: int, page: int):
    """Display a specific page of subjects"""
    session = user_sessions.get(user_id)
    if not session or session['type'] != 'subjects':
        return
    
    subjects = session['data']
    total = session['total']
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total)
    current_subjects = subjects[start_idx:end_idx]
    
    total_pages = math.ceil(total / ITEMS_PER_PAGE)
    
    # Create message
    message = f"*📚 Subjects in ABVV University (Page {page + 1}/{total_pages})*\n\n"
    for idx, subject in enumerate(current_subjects, start_idx + 1):
        message += f"{idx}. {subject}\n"
    
    message += f"\n*Total Subjects:* {total}"
    
    # Create inline keyboard for pagination
    keyboard = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"subjects_page_{page - 1}"))
    if end_idx < total:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"subjects_page_{page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Add search tip
    keyboard.append([InlineKeyboardButton("🔍 Search a Subject", switch_inline_query_current_chat="")])
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if page == 0:
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)

async def branches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all available branches"""
    branches = sorted(list(set(item.get("branch", "Unknown") for item in data)))
    
    if branches:
        response = "*🏫 Available Branches in ABVV:*\n\n"
        for branch in branches:
            # Count papers in this branch
            count = sum(1 for item in data if item.get("branch") == branch)
            response += f"• {branch} *({count} papers)*\n"
        response += f"\n*Total:* {len(branches)} branches"
    else:
        response = "No branches found in database."
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search and display papers based on user input with pagination"""
    text = update.message.text.lower()
    
    if not data:
        await update.message.reply_text("⚠️ Paper database is empty. Please contact administrator.")
        return
    
    # Search for matching papers
    results = []
    for item in data:
        subject_name = item.get("subject_name", "").lower()
        branch = item.get("branch", "").lower()
        
        if text in subject_name or text in branch:
            results.append(item)
    
    if not results:
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
        return
    
    # Store search results in user session
    user_id = update.effective_user.id
    user_sessions[user_id] = {
        'type': 'search',
        'data': results,
        'total': len(results),
        'search_term': text
    }
    
    # Show first page of results
    await show_search_results(update, user_id, 0)

async def show_search_results(update: Update, user_id: int, page: int):
    """Display a specific page of search results"""
    session = user_sessions.get(user_id)
    if not session or session['type'] != 'search':
        return
    
    results = session['data']
    total = session['total']
    search_term = session.get('search_term', '')
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total)
    current_results = results[start_idx:end_idx]
    
    total_pages = math.ceil(total / ITEMS_PER_PAGE)
    
    # Create message
    message = f"🔍 *Search Results for '{search_term}'* (Page {page + 1}/{total_pages})\n"
    message += f"📚 *Found {total} paper(s) in ABVV:*\n\n"
    
    for idx, item in enumerate(current_results, start_idx + 1):
        subject = item.get('subject_name', 'N/A')
        branch = item.get('branch', 'N/A')
        url = item.get('url', '#')
        
        message += f"*{idx}. {subject}*\n"
        message += f"   📚 *Branch:* {branch}\n"
        message += f"   🔗 [Download Link]({url})\n\n"
    
    # Create inline keyboard for pagination
    keyboard = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"search_page_{page - 1}"))
    if end_idx < total:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"search_page_{page + 1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Add navigation info
    if total > ITEMS_PER_PAGE:
        info_text = f"Showing {start_idx + 1}-{end_idx} of {total} results"
        keyboard.append([InlineKeyboardButton(info_text, callback_data="noop")])
    
    # Add new search button
    keyboard.append([InlineKeyboardButton("🔍 New Search", switch_inline_query_current_chat="")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if page == 0:
        await update.message.reply_text(message, parse_mode='Markdown', 
                                       disable_web_page_preview=True, 
                                       reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(message, parse_mode='Markdown', 
                                                      disable_web_page_preview=True, 
                                                      reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks for pagination"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("subjects_page_"):
        # Handle subjects pagination
        page = int(data.split("_")[2])
        await show_subjects_page(update, user_id, page)
    
    elif data.startswith("search_page_"):
        # Handle search results pagination
        page = int(data.split("_")[2])
        await show_search_results(update, user_id, page)
    
    elif data == "noop":
        # Just acknowledge the button press
        pass

# START BOT
app = ApplicationBuilder().token(TOKEN).build()

# Add command handlers
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("subjects", subjects_command))
app.add_handler(CommandHandler("branches", branches_command))

# Add message handler for text searches
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Add callback handler for buttons
app.add_handler(CallbackQueryHandler(button_callback))

print("🤖 ABVV University Papers Bot is running with pagination...")
print(f"📚 Loaded {len(data)} papers from ABVV University")
print("✅ Features: Paginated search results, browseable subjects list")
print("✅ Commands: /start, /help, /subjects, /branches")
app.run_polling()
