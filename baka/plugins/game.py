# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - Combat, Protection, and Revive Logic

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
    get_active_protection, get_mention
)
from baka.database import users_collection, groups_collection

# --- 🛠️ HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    """Checks if economy is enabled. Sends alert if disabled."""
    if update.effective_chat.type == "private":
        return True
    
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        # Exact alert as per requested screenshot
        await update.message.reply_text("⚠️ For reopen use: /open")
        return False
    return True

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attempts to kill a target user."""
    if not await check_economy(update): return

    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    # Anonymous or Channel checks
    if attacker.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("❌ You cannot kill from an Anonymous or Channel account!")

    # Spam protection
    if time.time() - attacker_db.get("last_kill_timestamp", 0) < random.uniform(1, 3):
        return await update.message.reply_text("⏳ Please wait before killing again!")

    # Resolve Target
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ Who do you want to kill?")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])

    if target_user.is_bot or target_user.id == 1087968824:
        return await update.message.reply_text("🛡️ You cannot kill Bots or Anonymous admins!")

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    # Protection Check
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_user.first_name} is protected.")

    # Daily Limit Check
    if attacker_db.get("daily_kills", 0) >= KILL_LIMIT_DAILY and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🚫 Daily Limit ({KILL_LIMIT_DAILY}) reached!")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("🎯 Target is already dead.")

    # Execution
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
        f"💰 Earned: <code>{format_money(reward)}</code>", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Attempts to rob a user."""
    if not await check_economy(update): return

    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("🕵️‍♂️ Anonymous accounts cannot rob!")

    # Usage alert
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text(
            "❗ Usage: Reply with <code>/rob <amount></code>",
            parse_mode=ParseMode.HTML
        )

    target_msg = update.message.reply_to_message
    target_user = target_msg.from_user
    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if target_user.is_bot or target_user.id == 1087968824:
        return await update.message.reply_text("🏛️ This target does not have a wallet!")

    # Protection Check
    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text(f"🛡️ {target_user.first_name} is protected.")

    rob_amount = int(context.args[0]) if context.args[0].isdigit() else 0
    if rob_amount <= 0: return await update.message.reply_text("❌ Enter a valid amount!")
    
    if rob_amount > ROB_MAX_AMOUNT and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ Max rob limit: <code>{format_money(ROB_MAX_AMOUNT)}</code>")

    if target_db.get('balance', 0) < rob_amount:
        return await update.message.reply_text("📉 Target doesn't have enough money!")

    # Perform Robbery
    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount, "daily_robs": 1}})

    # Success output
    await update.message.reply_text(
        f"💰 Success! Looted <code>{format_money(rob_amount)}</code> from {html.escape(target_user.first_name)}!", 
        parse_mode=ParseMode.HTML
    )

# --- ❤️ REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Revives a dead user for a cost."""
    if not await check_economy(update): return

    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ User not found.")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])
    else:
        target_user = user

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)

    if target_db.get('status') == 'alive':
        return await update.message.reply_text(f"✅ {html.escape(target_user.first_name)} is already alive!")
        
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Revive costs: {format_money(REVIVE_COST)}")
    
    users_collection.update_one({"user_id": target_user.id}, {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>REVIVED!</b>\n👤 Target: {get_mention(target_user)}", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Activates protection shield for the user."""
    if not await check_economy(update): return

    user = update.effective_user
    user_db = users_collection.find_one({"user_id": user.id}) or ensure_user_exists(user)
    
    # Check if user provides time argument
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /protect 1d")

    choice = context.args[0].lower()
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"❌ You need {format_money(cost)} to buy protection.")
    
    # Update Protection
    expiry_time = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$set": {"protection_expiry": expiry_time}, "$inc": {"balance": -cost}}
    )
    
    # Requested Output
    await update.message.reply_text("✅ You are protected now.")
