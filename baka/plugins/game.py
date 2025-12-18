# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Dual Protection (Rob & Kill)

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_time, format_money, stylize_text
)
from baka.database import users_collection

# --- Helper: Clickable Name (ID Hidden) ---
def get_clean_mention(user_id, name):
    return f"<a href='tg://user?id={user_id}'><b><i>{name}</i></b></a>"

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    target_db, error = await resolve_target(update, context)
    if not target_db: return await update.message.reply_text(error or "⚠️ Tag someone.")

    target_mention = get_clean_mention(target_db['user_id'], target_db.get('title', 'User'))

    # Protection Check
    expiry = get_active_protection(target_db)
    if expiry:
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}", 
            parse_mode=ParseMode.HTML
        )

    # Logic execute...
    await update.message.reply_text(f"🔪 {target_mention} killed!", parse_mode=ParseMode.HTML)

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_db, error = await resolve_target(update, context)
    if not target_db: return await update.message.reply_text(error or "⚠️ Tag someone.")

    target_mention = get_clean_mention(target_db['user_id'], target_db.get('title', 'User'))

    # Protection Check
    expiry = get_active_protection(target_db)
    if expiry:
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}", 
            parse_mode=ParseMode.HTML
        )

    # Logic execute...
    await update.message.reply_text(f"👤 Robbed from {target_mention}!", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND (Missing Function) ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fix for AttributeError: module 'game' has no attribute 'protect'"""
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(PROTECT_1D_COST)} {stylize_text('for Shield.')}")

    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection": expiry}, "$inc": {"balance": -PROTECT_1D_COST}}
    )

    await update.message.reply_text(
        f"🛡️ <b>{stylize_text('SHIELD ON')}!</b>\n\n"
        f"👤 {get_clean_mention(user.id, user.first_name)} {stylize_text('is protected from Rob & Kill for 24h!')}", 
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive"}})
    await update.message.reply_text("❤️ Revived!")
