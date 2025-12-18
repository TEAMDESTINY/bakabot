# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Baka Style Dual Protection

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

# --- Helper: Clickable Name (Baka Style) ---
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

    # --- 🛡️ PROTECTION BLOCK (KILL) ---
    expiry = get_active_protection(target_db)
    if expiry:
        rem = expiry - datetime.utcnow()
        # Baka Bot Style: Direct Block Message with Time
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}\n"
            f"⏳ {stylize_text('Protection left')}: <code>{format_time(rem)}</code>", 
            parse_mode=ParseMode.HTML
        )

    # Status Checks
    if target_db.get('user_id') == OWNER_ID: 
        return await update.message.reply_text(f"🙊 <b>{stylize_text('Senpai Shield!')}</b>")
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")

    # Execution
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
    
    if not context.args: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/rob 100</code>")
    
    try: amount = int(context.args[0])
    except: return

    target_db, error = await resolve_target(update, context)
    if not target_db: return

    target_mention = get_clean_mention(target_db['user_id'], target_db.get('name', 'User'))

    # --- 🛡️ PROTECTION BLOCK (ROB) ---
    expiry = get_active_protection(target_db)
    if expiry:
        rem = expiry - datetime.utcnow()
        # Baka Bot Style: Direct Block Message with Time
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}\n"
            f"⏳ {stylize_text('Protection left')}: <code>{format_time(rem)}</code>", 
            parse_mode=ParseMode.HTML
        )

    if target_db.get('balance', 0) < amount: 
        return await update.message.reply_text(f"📉 {target_mention} {stylize_text('ke paas itne paise nahi hain.')}", parse_mode=ParseMode.HTML)

    # Execution
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
    
    # Choice: 1 Day or 2 Day (Example using context args)
    days = 1
    cost = PROTECT_1D_COST
    if context.args and context.args[0] == "2":
        days = 2
        cost = PROTECT_1D_COST * 1.8 # Discounted rate for 2 days

    if user_db.get('balance', 0) < cost:
        return await update.message.reply_text(f"❌ {stylize_text('Low Balance')}! Need {format_money(cost)}")

    expiry = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection": expiry}, "$inc": {"balance": -cost}}
    )

    await update.message.reply_text(
        f"🛡️ <b>{stylize_text('SHIELD ACTIVATED')}!</b>\n\n"
        f"👤 {get_clean_mention(user.id, user.first_name)} {stylize_text('is now protected for')} {days} {stylize_text('day(s)')}!", 
        parse_mode=ParseMode.HTML
    )
