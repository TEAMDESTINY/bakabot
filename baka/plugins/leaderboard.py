# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Leaderboard - Clickable Mentions & HTML Safety Sync

import html
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import users_collection
from baka.utils import format_money, stylize_text

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Attribute fix for Ryan.py.
    Displays the top 10 richest users with clickable mentions.
    """
    # 1. Database se top 10 richest users uthana
    top_users = users_collection.find().sort("balance", -1).limit(10)
    
    msg = f"🌍 <b>{stylize_text('GLOBAL TOP 10')}</b> 🌍\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    count = 1
    for user in top_users:
        user_id = user.get("user_id")
        balance = format_money(user.get("balance", 0))
        
        # 2. Name safety logic (Pehle database wala name, fir fallback)
        raw_name = user.get("name") or user.get("first_name") or "User"
        
        # 3. HTML Clean karo taaki special characters se bot crash na ho
        safe_name = html.escape(str(raw_name))
        
        # 4. Clickable Mention Link banao
        if user_id:
            mention = f'<a href="tg://user?id={user_id}">{safe_name}</a>'
        else:
            mention = safe_name

        # 5. Ranking Badges
        if count == 1: badge = "🥇"
        elif count == 2: badge = "🥈"
        elif count == 3: badge = "🥉"
        else: badge = f"<code>{count}.</code>"
        
        msg += f"{badge} {mention} » <b>{balance}</b>\n"
        count += 1
        
    msg += "\n━━━━━━━━━━━━━━━━━━━━"
    
    # 6. Final response bhejna
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
