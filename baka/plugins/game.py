# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Mirror Game Plugin - Dynamic Name & Order Fix

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

# --- 💰 ROB COMMAND (DYNAMIC NAME & ORDER FIX) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sender_db = ensure_user_exists(user)

    # Target identify karna
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db, err = await resolve_target(update, context) if not target_user else (ensure_user_exists(target_user), None)

    if not target_db: 
        return await update.message.reply_text("❌ Victim nahi mila!")

    # Target ka current name nikalna
    target_display_name = target_user.first_name if target_user else target_db.get('name', "User")

    # 1. 🛡️ PROTECTION CHECK (Sabse Pehle)
    if is_protected(target_db) and user.id != OWNER_ID:
        # Output format jaisa aapne manga:
        return await update.message.reply_text(
            f"🛡️ 𝖥 {target_display_name} is protected.", 
            parse_mode=ParseMode.HTML
        )

    # 2. STATUS & BALANCE CHECK
    if target_db.get('status') == 'dead':
        return await update.message.reply_text(f"⚰️ {target_display_name} pehle se mara hua hai!")

    target_bal = target_db.get('balance', 0)
    if target_bal < 100: 
        return await update.message.reply_text(f"📉 {target_display_name} bahut gareeb hai!")

    # 3. 🎲 SUCCESS CHANCE (40% Chance)
    if random.randint(1, 100) <= 40:
        # Partial Loot (30% to 70%)
        loot_percent = random.randint(30, 70)
        loot_amount = int(target_bal * (loot_percent / 100))
        
        users_collection.update_one({"user_id": target_db["user_id"]}, {"$inc": {"balance": -loot_amount}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot_amount}})

        await update.message.reply_text(
            f"💰 <b>Success!</b>\nAapne {target_display_name} se <b>{format_money(loot_amount)}</b> ({loot_percent}%) loot liye!", 
            parse_mode=ParseMode.HTML
        )
    else:
        # 4. 💀 FAIL MESSAGE (Fine logic)
        fine = random.randint(200, 500)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(
            f"💀 <b>Failed!</b>\nAap pakde gaye aur <b>{format_money(fine)}</b> jurmana bharna pada.",
            parse_mode=ParseMode.HTML
        )

# --- ❤️ REVIVE (STABLE) ---
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

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db = ensure_user_exists(target_user) if target_user else (await resolve_target(update, context))[0]
    
    if not target_db: return await update.message.reply_text("❌ User not found.")

    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ Target protected hai!")

    reward = random.randint(150, 300)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": datetime.utcnow()}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward}})
    await update.message.reply_text(f"🔪 Killed! Reward: {format_money(reward)}")

# --- 🛡️ PROTECT ---
async def protect(update, context):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < PROTECT_1D_COST: return await update.message.reply_text("❌ Low balance!")
    expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -PROTECT_1D_COST}})
    await update.message.reply_text(f"🛡️ <b>Shield Activated!</b>", parse_mode=ParseMode.HTML)
