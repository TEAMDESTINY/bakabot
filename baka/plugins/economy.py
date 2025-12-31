# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Aesthetic Output Sync

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, get_mention, format_money, resolve_target, stylize_text
from baka.database import users_collection

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks wallet balance and stats in the requested format."""
    target_db, error = await resolve_target(update, context)
    
    if not target_db and error == "No target": 
        target_db = ensure_user_exists(update.effective_user)
    elif not target_db: 
        return await update.message.reply_text(f"❌ {error}", parse_mode=ParseMode.HTML)

    # 1. Data Preparation
    real_name = target_db.get('name', "User")
    bal = target_db.get('balance', 0)
    
    # 2. Global Rank Logic
    # Count how many users have more balance to determine the rank
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    # 3. Status Display Logic
    status = target_db.get('status', 'alive')
    status_text = "dead" if status == "dead" else "alive"
    kills = target_db.get('kills', 0)
    
    # 4. Final Aesthetic Output
    msg = (
        f"👤 <b>Name:</b> {html.escape(real_name)}\n"
        f"💰 <b>Total Balance:</b> <code>{format_money(bal)}</code>\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
        f"❤️ <b>Status:</b> {status_text}\n"
        f"⚔️ <b>Kills:</b> {kills}"
    )
    
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
