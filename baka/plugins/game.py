# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Mirror Game Plugin - 100% Fixed Protection & Partial Loot Logic

import random
import html
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, get_active_protection, 
    format_money, stylize_text, get_mention, is_protected,
    notify_victim, is_inspector, format_time
)
from baka.database import users_collection

# --- 👮 INSPECTOR & INTELLIGENCE ---
async def approve_inspector(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return 
    target_db, error = await resolve_target(update, context)
    if not target_db:
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: /approve 1d @username")
    time_arg = context.args[0] if context.args else "1d"
    match = re.search(r'(\d+)([dh])', time_arg.lower())
    amount, unit = (int(match.group(1)), match.group(2)) if match else (1, 'd')
    expiry = datetime.utcnow() + (timedelta(days=amount) if unit == 'd' else timedelta(hours=amount))
    users_collection.update_one({"user_id": target_db['user_id']}, {"$set": {"inspector_expiry": expiry}})
    await update.message.reply_text(f"✅ {get_mention(target_db)} {stylize_text('Approved')} for {time_arg}!", parse_mode=ParseMode.HTML)

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]
    
    if not target_db: return await update.message.reply_text("❌ User not found.")

    # 🛡️ PROTECTION CHECK (Strict)
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {get_mention(target_db)} is protected!", parse_mode=ParseMode.HTML)
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text(f"💀 Pehle khud revive ho jao!")
    
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {get_mention(target_db)} is already dead!", parse_mode=ParseMode.HTML)

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward}})
    await update.message.reply_text(f"🔪 {get_mention(attacker)} killed {get_mention(target_db)}!\n💰 +{format_money(reward)}", parse_mode=ParseMode.HTML)

# --- 💰 ROB COMMAND (FIXED SHIELD BYPASS) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sender_db = ensure_user_exists(user)
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]

    if not target_db: return await update.message.reply_text("❌ Victim not found.")

    # 🔥 🛡️ ABSOLUTE PROTECTION CHECK (Must be first)
    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {get_mention(target_db)} is protected by a shield!", parse_mode=ParseMode.HTML)

    target_bal = target_db.get('balance', 0)
    if target_bal < 100: return await update.message.reply_text(f"📉 Too broke!")

    # 🎲 Success Logic (40% Chance)
    if random.randint(1, 100) <= 40:
        # 💸 Balanced Loot (30% to 70%)
        loot_percent = random.randint(30, 70)
        loot_amount = int(target_bal * (loot_percent / 100))
        
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -loot_amount}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot_amount}})
        
        await update.message.reply_text(
            f"💰 <b>Success!</b>\nLooted <b>{format_money(loot_amount)}</b> ({loot_percent}%) from {get_mention(target_db)}!", 
            parse_mode=ParseMode.HTML
        )
    else:
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 <b>Failed!</b>\nAap pakde gaye aur <b>{format_money(fine)}</b> jurmana bharna pada.")

# --- ❤️ REVIVE ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('status') == 'alive': 
        return await update.message.reply_text("✨ You are already alive!")
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive cost: {format_money(REVIVE_COST)}")
    
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None}, "$inc": {"balance": -REVIVE_COST}}
    )
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT ---
async def protect(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: return await update.message.reply_text("❌ Low balance!")
    
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>Shield Activated!</b> (1 Day)", parse_mode=ParseMode.HTML)
