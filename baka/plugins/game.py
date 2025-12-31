# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Full English | Username Fix | No Mentions

import random
import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import (
    PROTECT_1D_COST, PROTECT_2D_COST, 
    REVIVE_COST, OWNER_ID, AUTO_REVIVE_HOURS
)
from baka.utils import (
    ensure_user_exists, resolve_target, format_money, 
    stylize_text, is_protected, notify_victim,
    get_active_protection
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND (Username & Reply Fixed) ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)

    # 🚨 FIX: Agar reply hai toh pehle use hi target maano (Ignore username suffix)
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_db = ensure_user_exists(target_user)
    else:
        # Agar reply nahi hai toh command ke peeche waale text se resolve karo
        target_db, err = await resolve_target(update, context)
        target_user = None # database se name nikalenge niche
    
    if not target_db:
        return await update.message.reply_text("⚠️ Please reply to someone to kill them.")

    # Status check
    if target_db.get('status') == 'dead':
        return await update.message.reply_text("<b>this user is already dead</b>", parse_mode=ParseMode.HTML)

    # Protection & Owner bypass logic
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Protected users cannot be killed.")
    
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text("💀 Please revive yourself first!")

    # Reward & 5-Hour Timer
    reward = random.randint(100, 200)
    revive_time = datetime.utcnow() + timedelta(hours=AUTO_REVIVE_HOURS)

    users_collection.update_one(
        {"user_id": target_db["user_id"]}, 
        {"$set": {"status": "dead", "death_time": datetime.utcnow(), "auto_revive_at": revive_time}}
    )
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1}})

    # Formatting Names Safely
    k_name = html.escape(attacker.first_name)
    v_name = html.escape(target_user.first_name if target_user else target_db.get('name', "User"))

    await update.message.reply_text(
        f"👤 {k_name} killed {v_name}!\n"
        f"💰 <b>Earned:</b> <code>{format_money(reward)}</code>",
        parse_mode=ParseMode.HTML
    )
    await notify_victim(context.bot, target_db['user_id'], f"☠️ You were killed by {k_name}!")

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user_exists(user)

    if not update.message.reply_to_message:
        return await update.message.reply_text("❗ <b>Usage:</b> Reply with <code>/rob &lt;amount&gt;</code>", parse_mode=ParseMode.HTML)

    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("❗ <b>Usage:</b> Reply with <code>/rob &lt;amount&gt;</code>", parse_mode=ParseMode.HTML)

    target_user = update.message.reply_to_message.from_user
    target_db = ensure_user_exists(target_user)
    rob_amount = int(context.args[0])

    if target_user.id == user.id:
        return await update.message.reply_text("🙄 You cannot rob yourself!")

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Protected users cannot be robbed.")

    target_bal = target_db.get('balance', 0)
    if target_bal < rob_amount:
        return await update.message.reply_text(f"📉 Target only has {format_money(target_bal)}!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount}})

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
    
    users_collection.update_one(
        {"user_id": target.id}, 
        {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}}
    )
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    expiry = get_active_protection(user_db)
    if expiry:
        remaining = expiry - datetime.utcnow()
        return await update.message.reply_text(
            f"🛡️ <b>Protected!</b>\n⏳ <b>Remaining:</b> <code>{remaining.days}d {remaining.seconds // 3600}h</code>", 
            parse_mode=ParseMode.HTML
        )
    
    choice = context.args[0] if context.args else "1d"
    days = 2 if choice == "2d" else 1
    cost = PROTECT_2D_COST if days == 2 else PROTECT_1D_COST

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"❌ Low balance! Needs {format_money(cost)}.")
    
    new_expiry = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection_expiry": new_expiry}, "$inc": {"balance": -cost}}
    )
    await update.message.reply_text(f"🛡️ <b>Shield Activated</b> for {days} day(s)!", parse_mode=ParseMode.HTML)
