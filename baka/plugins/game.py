# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Anti-Spam, Daily Limits & Username Fix

import random
import html
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import (
    PROTECT_1D_COST, PROTECT_2D_COST, 
    REVIVE_COST, OWNER_ID, AUTO_REVIVE_HOURS,
    KILL_LIMIT_DAILY, ROB_LIMIT_DAILY, ROB_MAX_AMOUNT
)
from baka.utils import (
    ensure_user_exists, resolve_target, format_money, 
    stylize_text, is_protected, notify_victim,
    get_active_protection
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND (100/Day Limit + 1-3s Anti-Spam) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    # 🚨 ANTI-SPAM COOLDOWN (1-3 Seconds)
    last_kill_time = attacker_db.get("last_kill_timestamp", 0)
    cooldown_interval = random.uniform(1, 3) 
    if time.time() - last_kill_time < cooldown_interval:
        return await update.message.reply_text("⏳ <b>Anti-Spam!</b> Please wait a moment before killing again.")

    # 🚨 DAILY LIMIT RESET & CHECK (100 Kills)
    last_reset = attacker_db.get("limit_reset_date", now)
    if now > last_reset + timedelta(days=1):
        users_collection.update_one(
            {"user_id": attacker.id}, 
            {"$set": {"daily_kills": 0, "daily_robs": 0, "limit_reset_date": now}}
        )
        attacker_db["daily_kills"] = 0
    
    if attacker_db.get("daily_kills", 0) >= KILL_LIMIT_DAILY and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🚫 <b>Daily Limit Reached!</b>\nYou can only kill {KILL_LIMIT_DAILY} users per day.")

    # Target Selection (Priority to Reply)
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_db = ensure_user_exists(target_user)
    else:
        target_db, err = await resolve_target(update, context)
        target_user = None 
    
    if not target_db:
        return await update.message.reply_text("⚠️ Please reply to someone to kill them.")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("<b>this user is already dead</b>", parse_mode=ParseMode.HTML)

    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Protected users cannot be killed.")
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text("💀 Please revive yourself first!")

    # Reward & Process
    reward = random.randint(100, 200)
    revive_time = now + timedelta(hours=AUTO_REVIVE_HOURS)

    users_collection.update_one(
        {"user_id": target_db["user_id"]}, 
        {"$set": {"status": "dead", "death_time": now, "auto_revive_at": revive_time}}
    )
    users_collection.update_one(
        {"user_id": attacker.id}, 
        {"$inc": {"balance": reward, "kills": 1, "daily_kills": 1}, "$set": {"last_kill_timestamp": time.time()}}
    )

    k_name = html.escape(attacker.first_name)
    v_name = html.escape(target_user.first_name if target_user else target_db.get('name', "User"))

    await update.message.reply_text(
        f"👤 {k_name} killed {v_name}!\n💰 Earned: <code>{format_money(reward)}</code>",
        parse_mode=ParseMode.HTML
    )
    await notify_victim(context.bot, target_db['user_id'], f"☠️ You were killed by {k_name}!")

# --- 💰 ROB COMMAND (200/Day Limit + 5 Lakh Max) ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get("daily_robs", 0) >= ROB_LIMIT_DAILY and user.id != OWNER_ID:
        return await update.message.reply_text(f"🚫 <b>Daily Limit Reached!</b> ({ROB_LIMIT_DAILY} robs/day).")

    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with <code>/rob <amount></code>", parse_mode=ParseMode.HTML)

    if not context.args[0].isdigit():
        return await update.message.reply_text("❌ Enter a valid amount!")

    rob_amount = int(context.args[0])

    # 🚨 MAX ROB LIMIT (5 Lakh)
    if rob_amount > ROB_MAX_AMOUNT and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ <b>Limit Exceeded!</b>\nYou can only rob up to <code>{format_money(ROB_MAX_AMOUNT)}</code>.")

    target_user = update.message.reply_to_message.from_user
    target_db = ensure_user_exists(target_user)

    if target_user.id == user.id:
        return await update.message.reply_text("🙄 You cannot rob yourself!")

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Protected users cannot be robbed.")

    target_bal = target_db.get('balance', 0)
    if target_bal < rob_amount:
        return await update.message.reply_text(f"📉 Target only has {format_money(target_bal)}!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount, "daily_robs": 1}})

    await update.message.reply_text(
        f"💰 <b>Success!</b> Looted <code>{format_money(rob_amount)}</code> from {html.escape(target_user.first_name)}!",
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else user
    target_db = ensure_user_exists(target)

    if target_db.get('status') == 'alive':
        return await update.message.reply_text(f"✅ ~ {html.escape(target.first_name)} is already alive!")
        
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive cost: {format_money(REVIVE_COST)}")
    
    users_collection.update_one({"user_id": target.id}, {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    expiry = get_active_protection(user_db)
    
    if expiry:
        remaining = expiry - datetime.utcnow()
        return await update.message.reply_text(f"🛡️ <b>Protected!</b>\n⏳ Remaining: <code>{remaining.days}d {remaining.seconds // 3600}h</code>", parse_mode=ParseMode.HTML)
    
    choice = context.args[0] if context.args else "1d"
    days = 2 if choice == "2d" else 1
    cost = PROTECT_2D_COST if days == 2 else PROTECT_1D_COST

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"❌ Low balance! Needs {format_money(cost)}.")
    
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": datetime.utcnow() + timedelta(days=days)}, "$inc": {"balance": -cost}})
    await update.message.reply_text(f"🛡️ <b>Shield Activated</b> for {days} day(s)!", parse_mode=ParseMode.HTML)
