# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Full English Output & 6h Auto-Revive

import random
import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import PROTECT_1D_COST, REVIVE_COST, OWNER_ID
from baka.utils import (
    ensure_user_exists, resolve_target, format_money, 
    stylize_text, is_protected, notify_victim,
    get_active_protection
)
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    target_db, err = (ensure_user_exists(target_user), None) if target_user else await resolve_target(update, context)
    
    if not target_db:
        return await update.message.reply_text("⚠️ Please reply to someone to kill them.")

    # 1. Already Dead Check (English Output)
    if target_db.get('status') == 'dead':
        return await update.message.reply_text("<b>this user is already dead</b>", parse_mode=ParseMode.HTML)

    # 2. Protection Check
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Target is protected.")
    
    # 3. Attacker Status Check
    if attacker_db.get('status') == 'dead': 
        return await update.message.reply_text("💀 Please revive yourself first!")

    # 4. Logic & 6-Hour Timer
    reward = random.randint(100, 200)
    revive_time = datetime.utcnow() + timedelta(hours=6)

    users_collection.update_one(
        {"user_id": target_db["user_id"]}, 
        {"$set": {"status": "dead", "death_time": datetime.utcnow(), "auto_revive_at": revive_time}}
    )
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1}})

    # 5. Plain Text Output (No Mentions)
    k_name = attacker.first_name
    v_name = target_user.first_name if target_user else target_db.get('name', "User")

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
        return await update.message.reply_text("❌ <b>Usage:</b> Reply to someone with <code>/rob [amount]</code>")

    target_user = update.message.reply_to_message.from_user
    target_db = ensure_user_exists(target_user)

    if target_user.id == user.id:
        return await update.message.reply_text("🙄 You cannot rob yourself!")

    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("⚠️ Please specify an amount! Example: <code>/rob 3282</code>")
    
    rob_amount = int(context.args[0])
    target_bal = target_db.get('balance', 0)

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Target is protected!")

    if target_bal < rob_amount:
        return await update.message.reply_text(f"📉 Target only has {format_money(target_bal)}!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount}})

    v_name = target_user.first_name
    await update.message.reply_text(
        f"💰 <b>Success!</b> Looted <code>{format_money(rob_amount)}</code> from {v_name}!",
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('status') == 'alive':
        return await update.message.reply_text(f"✅ ~ {user.first_name} is already alive!", parse_mode=ParseMode.HTML)
        
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive cost: {format_money(REVIVE_COST)}")
    
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}, "$inc": {"balance": -REVIVE_COST}}
    )
    await update.message.reply_text(f"❤️ <b>{stylize_text('REVIVED')}!</b>", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    expiry = get_active_protection(user_db)
    if expiry:
        remaining = expiry - datetime.utcnow()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        timer_text = f"{days}d {hours}h {minutes}m"
        return await update.message.reply_text(
            f"🛡️ <b>You are already protected!</b>\n⏳ <b>Remaining:</b> <code>{timer_text}</code>",
            parse_mode=ParseMode.HTML
        )
    
    if user_db.get('balance', 0) < PROTECT_1D_COST: 
        return await update.message.reply_text("❌ Low balance for Protect!")
    
    new_expiry = datetime.utcnow() + timedelta(days=1)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection_expiry": new_expiry}, "$inc": {"balance": -PROTECT_1D_COST}}
    )
    await update.message.reply_text(f"🛡️ <b>{stylize_text('Protection Activated')}!</b>\nYou are protected", parse_mode=ParseMode.HTML)
