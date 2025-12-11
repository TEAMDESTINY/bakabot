from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import users_collection
from baka.utils import format_money, stylize_text
import html # Name clean karne ke liye (taaki error na aaye)

async def global_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Top 10 users dhoondo
    top_users = users_collection.find().sort("balance", -1).limit(10)
    
    msg = f"🌍 <b>{stylize_text('GLOBAL TOP 10')}</b> 🌍\n\n"
    
    count = 1
    for user in top_users:
        user_id = user.get("user_id")
        balance = format_money(user.get("balance", 0))
        
        # 1. Name dhoondo (Pehle first_name, nahi toh name, nahi toh "User")
        raw_name = user.get("first_name") or user.get("name") or "User"
        
        # 2. HTML Error se bachne ke liye name clean karo (< > symbols hatana)
        safe_name = html.escape(str(raw_name))
        
        # 3. Clickable Mention banao
        if user_id:
            mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'
        else:
            mention = safe_name # Agar ID nahi hai toh simple text

        # 4. Badges add karo
        if count == 1: badge = "🥇"
        elif count == 2: badge = "🥈"
        elif count == 3: badge = "🥉"
        else: badge = f"<code>{count}.</code>"
        
        msg += f"{badge} {mention} » <b>{balance}</b>\n"
        count += 1
        
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
