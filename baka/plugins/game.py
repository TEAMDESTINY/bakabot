# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - Combat & Revive Logic ($500 Cost)

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
    stylize_text, is_protected, get_mention
)
from baka.database import users_collection, groups_collection

# --- 🛠️ HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    if update.effective_chat.type == "private":
        return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("⚠️ For reopen use: /open")
        return False
    return True

# --- ❤️ REVIVE COMMAND (Cost: $500) ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Revives a dead user for a fixed cost of $500."""
    if not await check_economy(update): return

    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    # Target determine karein (Reply ya Self)
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ User not found.")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])
    else:
        target_user = user

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)

    # Check if already alive
    if target_db.get('status') == 'alive':
        return await update.message.reply_text(f"✅ {html.escape(target_user.first_name)} is already alive!")
        
    # Balance check for $500 cost
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive costs: {format_money(REVIVE_COST)}")
    
    # Database execution
    users_collection.update_one(
        {"user_id": target_user.id}, 
        {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}}
    )
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$inc": {"balance": -REVIVE_COST}}
    )

    # Final English Output
    await update.message.reply_text(
        f"❤️ <b>REVIVED!</b>\n"
        f"👤 Target: {get_mention(target_user)}\n"
        f"💰 Fee: {format_money(REVIVE_COST)} deducted.", 
        parse_mode=ParseMode.HTML
    )

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attempts to kill a target user with cooldown and protection checks."""
    if not await check_economy(update): return
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    # Anonymous check
    if attacker.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("❌ Anonymous accounts cannot kill!")

    # Spam protection
    if time.time() - attacker_db.get("last_kill_timestamp", 0) < 2:
        return await update.message.reply_text("⏳ Wait before killing again!")

    # Resolve Target
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_db_raw, err = await resolve_target(update, context)
        if target_db_raw:
            target_user = await context.bot.get_chat(target_db_raw['user_id'])
    
    if not target_user: return await update.message.reply_text("⚠️ Who do you want to kill?")
    if target_user.is_bot: return await update.message.reply_text("🛡️ You cannot kill Bots!")

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    # Protection Check
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_user.first_name} is protected.")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("🎯 Target is already dead.")

    # Kill execution
    reward = random.randint(100, 200)
    users_collection.update_one(
        {"user_id": target_user.id}, 
        {"$set": {"status": "dead", "death_time": now, "auto_revive_at": now + timedelta(hours=AUTO_REVIVE_HOURS)}}
    )
    users_collection.update_one(
        {"user_id": attacker.id}, 
        {"$inc": {"balance": reward, "kills": 1, "daily_kills": 1}, "$set": {"last_kill_timestamp": time.time()}}
    )

    await update.message.reply_text(
        f"👤 {html.escape(attacker.first_name)} killed {html.escape(target_user.first_name)}!\n"
        f"💰 Earned: {format_money(reward)}", 
        parse_mode=ParseMode.HTML
    )

# --- (Rob and Protect logic remains same as provided) ---
