# baka/plugins/leaderboard.py

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import users_collection
from baka.utils import format_money, get_mention, stylize_text

async def global_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Top 10 users ko balance ke hisab se dhoondo
    top_users = users_collection.find().sort("balance", -1).limit(10)
    
    msg = f"🌍 <b>{stylize_text('GLOBAL TOP 10')}</b> 🌍\n\n"
    
    count = 1
    async for user in top_users:
        # User ka naam ya mention ready karo
        name = user.get("first_name", "Unknown")
        balance = format_money(user.get("balance", 0))
        
        # Emoji logic
        if count == 1: badge = "🥇"
        elif count == 2: badge = "🥈"
        elif count == 3: badge = "🥉"
        else: badge = f"<code>{count}.</code>"
        
        msg += f"{badge} {name} » <b>{balance}</b>\n"
        count += 1
        
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
