# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Destiny / Baka Bot (Optimized & Fixed)

import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_time, format_money, stylize_text, get_mention
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Reply or Tag to kill!')}", parse_mode=ParseMode.HTML)

    # Resolve target mention correctly
    target_mention = get_mention(target_db)

    # Protection Check
    expiry = get_active_protection(target_db)
    if expiry:
        rem_time = format_time(expiry - datetime.utcnow())
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}\n"
            f"⏳ {stylize_text('Time left')}: <code>{rem_time}</code>", 
            parse_mode=ParseMode.HTML
        )

    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 {stylize_text('Pehle khud revive ho jao!')}")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_mention} {stylize_text('is already dead!')}", parse_mode=ParseMode.HTML)

    # Success Logic
    reward = random.randint(100, 250)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker_obj.id}, {"$inc": {"kills": 1, "balance": reward}})

    await update.message.reply_text(
        f"🔪 {get_mention(attacker_obj)} {stylize_text('killed')} {target_mention}!\n"
        f"💰 <b>{stylize_text('Earned')}:</b> {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_obj = update.effective_user
    attacker_db = ensure_user_exists(attacker_obj)
    
    target_db, error = await resolve_target(update, context)
    if not target_db: return

    target_mention = get_mention(target_db)

    # Protection Check
    expiry = get_active_protection(target_db)
    if expiry:
        rem_time = format_time(expiry - datetime.utcnow())
        return await update.message.reply_text(
            f"🛡️ {target_mention} {stylize_text('is protected right now!')}\n"
            f"⏳ {stylize_text('Shield expires in')}: <code>{rem_time}</code>", 
            parse_mode=ParseMode.HTML
        )

    amount = random.randint(50, 200)
    if target_db.get('balance', 0) < amount: amount = target_db.get('balance', 0)

    if amount > 0:
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": attacker_obj.id}, {"$inc": {"balance": amount}})
        
        await update.message.reply_text(
            f"👤 {get_mention(attacker_obj)} {stylize_text('robbed')} <b>{format_money(amount)}</b> {stylize_text('from')} {target_mention}!", 
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(f"📉 {target_mention} {stylize_text('is already broke!')}", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('balance', 0) < PROTECT_1D_COST:
        return await update.message.reply_text(f"❌ {stylize_text('Need')} {format_money(PROTECT_1D_COST)} {stylize_text('for Shield.')}")

    # Set protection to 24 hours from now
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    
    await update.message.reply_text(
        f"🛡️ <b>{stylize_text('SHIELD ACTIVATED')}!</b>\n"
        f"👤 {get_mention(user)} {stylize_text('is protected for 24h.')}", 
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"❤️ <b>{stylize_text('REVIVED')}!</b>\n"
        f"👤 {get_mention(user)} {stylize_text('is back in the game!')}", 
        parse_mode=ParseMode.HTML
    )
