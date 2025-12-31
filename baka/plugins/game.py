# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Full English & Bonus System Sync

import html
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import DAILY_BONUS, BONUS_COOLDOWN
from baka.utils import (
    ensure_user_exists, format_money, 
    resolve_target, stylize_text
)
from baka.database import users_collection

# --- 💰 BALANCE COMMAND ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks wallet balance and stats in English."""
    target_db, error = await resolve_target(update, context)
    
    if not target_db and error == "No target": 
        target_db = ensure_user_exists(update.effective_user)
    elif not target_db: 
        return await update.message.reply_text(f"❌ {error}", parse_mode=ParseMode.HTML)

    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    msg = (
        f"👤 <b>Name:</b> {html.escape(target_db.get('name', 'User'))}\n"
        f"💰 <b>Total Balance:</b> <code>{format_money(bal)}</code>\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
        f"❤️ <b>Status:</b> {target_db.get('status', 'alive')}\n"
        f"⚔️ <b>Kills:</b> {target_db.get('kills', 0)}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🏆 MY RANK COMMAND ---
async def my_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quick check for global rank."""
    user_db = ensure_user_exists(update.effective_user)
    bal = user_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    await update.message.reply_text(f"🏆 <b>Your Global Rank:</b> {rank}", parse_mode=ParseMode.HTML)

# --- 🌍 TOP RICH COMMAND ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global Richest Leaderboard."""
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    
    msg = f"🏆 <b>{stylize_text('GLOBAL RICHEST')}</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » <code>{format_money(user.get('balance', 0))}</code>\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- ⚡ 12-HOUR BONUS SYSTEM ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claims $50 every 12 hours."""
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    last_claim = user_db.get("last_bonus_claim")
    now = datetime.utcnow()

    if last_claim:
        # Check if 12 hours have passed
        wait_until = last_claim + timedelta(hours=BONUS_COOLDOWN)
        if now < wait_until:
            remaining = wait_until - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return await update.message.reply_text(
                f"⏳ <b>Too soon!</b>\nYou can claim again in <code>{hours}h {minutes}m</code>.",
                parse_mode=ParseMode.HTML
            )

    users_collection.update_one(
        {"user_id": user.id},
        {"$inc": {"balance": DAILY_BONUS}, "$set": {"last_bonus_claim": now}}
    )
    await update.message.reply_text(
        f"🎁 <b>Bonus Claimed!</b>\nYou received <code>{format_money(DAILY_BONUS)}</code>.\n"
        f"Next claim in {BONUS_COOLDOWN} hours.",
        parse_mode=ParseMode.HTML
    )
