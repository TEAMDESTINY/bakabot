# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - Fixed AttributeError & Protection

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

    if attacker.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("❌ Anonymous ya Channel se kill nahi kar sakte!")

    if time.time() - attacker_db.get("last_kill_timestamp", 0) < random.uniform(1, 3):
        return await update.message.reply_text("⏳ Spam mat karo bhai!")

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_msg = update.message.reply_to_message
    else:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ Kise maarna hai?")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])
        target_msg = None

    if target_user.is_bot or target_user.id == 1087968824 or (target_msg and target_msg.sender_chat):
        return await update.message.reply_text("🛡️ Bots, Channels ya Anonymous ko nahi maar sakte!")

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if is_protected(target_db) and attacker.id != OWNER_ID:
        expiry = get_active_protection(target_db)
        remaining = expiry - now
        hours, _ = divmod(remaining.seconds, 3600)
        return await update.message.reply_text(
            f"🛡️ <b>Target protected hai!</b>\n⏳ Remaining: <code>{remaining.days}d {hours}h</code>",
            parse_mode=ParseMode.HTML
        )

    if attacker_db.get("daily_kills", 0) >= KILL_LIMIT_DAILY and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🚫 Daily Limit ({KILL_LIMIT_DAILY}) puri ho gayi!")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("🎯 Yeh pehle hi mar chuka hai.")

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
    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if target_user.is_bot or target_user.id == 1087968824 or target_msg.sender_chat:
        return await update.message.reply_text("🏛️ Is target ka wallet nahi hota!")

    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ Yeh user shield ke piche hai!")

    rob_amount = int(context.args[0]) if context.args[0].isdigit() else 0
    if rob_amount > ROB_MAX_AMOUNT and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ Max rob: <code>{format_money(ROB_MAX_AMOUNT)}</code>")

    if target_db.get('balance', 0) < rob_amount:
        return await update.message.reply_text("📉 Uske paas itna paisa nahi hai!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount, "daily_robs": 1}})

    await update.message.reply_text(f"💰 Looted <code>{format_money(rob_amount)}</code> from {html.escape(target_user.first_name)}!", parse_mode=ParseMode.HTML)

# --- ❤️ REVIVE COMMAND ---
# Iska Ryan.py mein handler: app_bot.add_handler(CommandHandler("revive", game.revive))
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: return await update.message.reply_text(err or "⚠️ User nahi mila.")
        target_user = await context.bot.get_chat(target_db_raw['user_id'])
    else:
        target_user = user

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)

    if target_db.get('status') == 'alive':
        return await update.message.reply_text(f"✅ {html.escape(target_user.first_name)} pehle se zinda hai!")
        
    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"❌ Cost: {format_money(REVIVE_COST)}")
    
    users_collection.update_one({"user_id": target_user.id}, {"$set": {"status": "alive", "death_time": None, "auto_revive_at": None}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"❤️ <b>REVIVED!</b>\n👤 Target: {get_mention(target_user)}", parse_mode=ParseMode.HTML)

# --- 🛡️ PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = users_collection.find_one({"user_id": user.id}) or ensure_user_exists(user)
    
    if is_protected(user_db):
        expiry = get_active_protection(user_db)
        remaining = expiry - datetime.utcnow()
        hours, _ = divmod(remaining.seconds, 3600)
        return await update.message.reply_text(f"🛡️ Protected! Baaki: <code>{remaining.days}d {hours}h</code>")
    
    choice = context.args[0] if context.args else "1d"
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"❌ Needs {format_money(cost)}.")
    
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": datetime.utcnow() + timedelta(days=days)}, "$inc": {"balance": -cost}})
    await update.message.reply_text(f"🛡️ Shield Activated for {days} day(s)!", parse_mode=ParseMode.HTML)
