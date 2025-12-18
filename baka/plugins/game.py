# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - All Handlers Included (Kill, Rob, Protect, Revive)

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
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    target_mention = get_clean_mention(target_db['user_id'], target_db.get('name', 'User'))

    # Protection Check
    if get_active_protection(target_db):
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected right now!')}", parse_mode=ParseMode.HTML)

    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")

    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(
        f"🔪 {get_clean_mention(attacker_obj.id, attacker_obj.first_name)} killed {target_mention}!\n"
        f"💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: return

    target_mention = get_clean_mention(target_db['user_id'], target_db.get('name', 'User'))

    if get_active_protection(target_db):
        return await update.message.reply_text(f"🛡️ {target_mention} {stylize_text('is protected right now!')}", parse_mode=ParseMode.HTML)

    amount = random.randint(50, 150)
    if target_db.get('balance', 0) < amount: amount = target_db.get('balance', 0)

    if amount > 0:
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": attacker_db["user_id"]}, {"$inc": {"balance": amount}})
    
    await update.message.reply_text(
        f"👤 {get_clean_mention(attacker_obj.id, attacker_obj.first_name)} robbed <b>{format_money(amount)}</b> from {target_mention}!", 
        parse_mode=ParseMode.HTML
    )

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Low Balance')}")

    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>{stylize_text('SHIELD ON')}!</b>", parse_mode=ParseMode.HTML)

# --- ❤️ REVIVE COMMAND (Fixed: Added Missing Function) ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Brings a dead player back to life for a cost."""
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('status') == 'alive':
        return await update.message.reply_text(f"✨ {stylize_text('You are already alive!')}")

    if user_db.get('balance', 0) < REVIVE_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(REVIVE_COST)} {stylize_text('to Revive.')}")

    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}}
    )

    await update.message.reply_text(
        f"❤️ <b>{stylize_text('REVIVED')}!</b>\n\n"
        f"👤 {get_clean_mention(user.id, user.first_name)} {stylize_text('is back from the dead!')}", 
        parse_mode=ParseMode.HTML
    )
