# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - Strict Protection & Fresh DB Query

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
from baka.database import users_collection

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    # 🛑 SENDER VALIDATION: No Anonymous/Channel Attacker
    if attacker.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("❌ Anonymous ya Channel se kill nahi kar sakte!")

    # Target Selection
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_msg = update.message.reply_to_message
    else:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ Kise maarna hai?")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])
        target_msg = None

    # 🛑 TARGET VALIDATION
    if target_user.is_bot or target_user.id == 1087968824 or (target_msg and target_msg.sender_chat):
        return await update.message.reply_text("🛡️ Bots, Channels ya Anonymous ko nahi maar sakte!")

    # 🛡️ FRESH DB PROTECTION CHECK (Bugs fixed here)
    # Variable 'target_db' ko hamesha database se fresh fetch karna zaroori hai
    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if is_protected(target_db) and attacker.id != OWNER_ID:
        expiry = get_active_protection(target_db)
        remaining = expiry - now
        hours, _ = divmod(remaining.seconds, 3600)
        return await update.message.reply_text(
            f"🛡️ <b>Target protected hai!</b>\n⏳ Remaining: <code>{remaining.days}d {hours}h</code>",
            parse_mode=ParseMode.HTML
        )

    # ... baaki ka logic (Daily limits/Status check) ...
    if target_db.get('status') == 'dead':
        return await update.message.reply_text("🎯 Yeh pehle hi mar chuka hai.")

    # Process Kill
    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_db["user_id"]}, {"$set": {"status": "dead", "death_time": now, "auto_revive_at": now + timedelta(hours=AUTO_REVIVE_HOURS)}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1, "daily_kills": 1}, "$set": {"last_kill_timestamp": time.time()}})

    await update.message.reply_text(f"👤 {html.escape(attacker.first_name)} killed {html.escape(target_user.first_name)}!\n💰 Earned: <code>{format_money(reward)}</code>", parse_mode=ParseMode.HTML)

# --- 💰 ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    now = datetime.utcnow()
    
    if user.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("🕵️‍♂️ Anonymous ya Channel se chori nahi hoti!")

    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with <code>/rob <amount></code>")

    target_msg = update.message.reply_to_message
    target_user = target_msg.from_user
    
    # 🛑 TARGET VALIDATION
    if target_user.is_bot or target_user.id == 1087968824 or target_msg.sender_chat:
        return await update.message.reply_text("🏛️ Is target ka wallet nahi hota!")

    # 🛡️ FRESH DB PROTECTION CHECK
    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if is_protected(target_db) and user.id != OWNER_ID:
        expiry = get_active_protection(target_db)
        remaining = expiry - now
        hours, _ = divmod(remaining.seconds, 3600)
        return await update.message.reply_text(
            f"🛡️ <b>Target protected hai!</b>\n⏳ Remaining: <code>{remaining.days}d {hours}h</code>",
            parse_mode=ParseMode.HTML
        )

    # ... baaki ka rob logic ...
    rob_amount = int(context.args[0]) if context.args[0].isdigit() else 0
    if target_db.get('balance', 0) < rob_amount:
        return await update.message.reply_text("📉 Uske paas itna paisa nahi hai!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount, "daily_robs": 1}})

    await update.message.reply_text(f"💰 Looted <code>{format_money(rob_amount)}</code> from {html.escape(target_user.first_name)}!", parse_mode=ParseMode.HTML)

# ... (revive aur protect functions waise hi rahenge) ...
