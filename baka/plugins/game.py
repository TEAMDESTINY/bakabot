# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Game Plugin - Strict Protection, Anti-Bot & Anti-Channel

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

# --- 🔪 KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    # 🛑 SENDER VALIDATION
    if attacker.id == 1087968824 or update.message.sender_chat:
        return await update.message.reply_text("❌ 𝙰𝚗𝚘𝚗𝚢𝚖𝚘𝚞𝚜 𝚢𝚊 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 𝚜𝚎 𝚔𝚒𝚕𝚕 𝚗𝚊𝚑𝚒 𝚔𝚊𝚛 𝚜𝚊𝚔𝚝𝚎!")

    # 🚨 ANTI-SPAM
    if time.time() - attacker_db.get("last_kill_timestamp", 0) < random.uniform(1, 3):
        return await update.message.reply_text("⏳ 𝚂𝚙𝚊𝚖 𝚖𝚊𝚝 𝚔𝚊𝚛𝚘 𝚋𝚑𝚊𝚒!")

    # Target Selection
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_msg = update.message.reply_to_message
        target_db = ensure_user_exists(target_user)
    else:
        target_db, err = await resolve_target(update, context)
        if not target_db: return await update.message.reply_text(err or "⚠️ 𝙺𝚒𝚜𝚎 𝚖𝚊𝚊𝚛𝚗𝚊 𝚑𝚊𝚒?")
        target_user = await context.bot.get_chat(target_db['user_id'])
        target_msg = None

    # 🛑 TARGET VALIDATION
    if target_user.is_bot or target_user.id == 1087968824 or (target_msg and target_msg.sender_chat):
        return await update.message.reply_text("🛡️ 𝙱𝚘𝚝𝚜, 𝙲𝚑𝚊𝚗𝚗𝚎𝚕𝚜 𝚢𝚊 𝙰𝚗𝚘𝚗𝚢𝚖𝚘𝚞𝚜 𝚔𝚘 𝚗𝚊𝚑𝚒 𝚖𝚊𝚊𝚛 𝚜𝚊𝚔𝚝𝚎!")

    # 🛡️ STRICT PROTECTION CHECK
    if is_protected(target_db) and attacker.id != OWNER_ID:
        expiry = get_active_protection(target_db)
        remaining = expiry - now
        return await update.message.reply_text(
            f"🛡️ 𝚃𝚊𝚛𝚐𝚎𝚝 𝚙𝚛𝚘𝚝𝚎𝚌𝚝𝚎𝚍 𝚑𝚊𝚒!\n⏳ 𝚁𝚎𝚖𝚊𝚒𝚗𝚒𝚗𝚐: <code>{remaining.days}d {remaining.seconds // 3600}h</code>",
            parse_mode=ParseMode.HTML
        )

    # 🚨 LIMITS
    if attacker_db.get("daily_kills", 0) >= KILL_LIMIT_DAILY and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"🚫 𝙳𝚊𝚒𝚕𝚢 𝙻𝚒𝚖𝚒𝚝 ({KILL_LIMIT_DAILY}) 𝚙𝚘𝚘𝚛𝚒 𝚑𝚘 𝚐𝚊𝚢𝚒!")

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("🎯 𝚈𝚎 𝚙𝚎𝚑𝚕𝚎 𝚑𝚒 𝚖𝚊𝚛 𝚌𝚑𝚞𝚔𝚊 𝚑𝚊𝚒.")

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
        return await update.message.reply_text("🕵️‍♂️ 𝙰𝚗𝚘𝚗𝚢𝚖𝚘𝚞𝚜 𝚢𝚊 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 𝚜𝚎 𝚌𝚑𝚘𝚛𝚒 𝚗𝚊𝚑𝚒 𝚑𝚘𝚝𝚒!")

    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ Usage: Reply with <code>/rob <amount></code>", parse_mode=ParseMode.HTML)

    target_msg = update.message.reply_to_message
    target_user = target_msg.from_user
    target_db = ensure_user_exists(target_user)
    
    # 🛑 TARGET VALIDATION
    if target_user.is_bot or target_user.id == 1087968824 or target_msg.sender_chat:
        return await update.message.reply_text("🏛️ 𝙸𝚜 𝚝𝚊𝚛𝚐𝚎𝚝 𝚔𝚊 𝚠𝚊𝚕𝚕𝚎𝚝 𝚗𝚊𝚑𝚒 𝚑𝚘𝚝𝚊!")

    # 🛡️ STRICT PROTECTION CHECK
    if is_protected(target_db) and user.id != OWNER_ID:
        return await update.message.reply_text("🛡️ 𝚈𝚎 𝚞𝚜𝚎𝚛 𝚜𝚑𝚒𝚎𝚕𝚍 𝚔𝚎 𝚙𝚒𝚌𝚑𝚎 𝚑𝚊𝚒, 𝚕𝚘𝚘𝚝 𝚗𝚊𝚑𝚒 𝚜𝚊𝚔𝚝𝚎!")

    rob_amount = int(context.args[0]) if context.args[0].isdigit() else 0
    if rob_amount > ROB_MAX_AMOUNT and user.id != OWNER_ID:
        return await update.message.reply_text(f"❌ 𝙼𝚊𝚡 𝚛𝚘𝚋 𝚕𝚒𝚖𝚒𝚝: <code>{format_money(ROB_MAX_AMOUNT)}</code>")

    if target_db.get('balance', 0) < rob_amount:
        return await update.message.reply_text("📉 𝚄𝚜𝚔𝚎 𝚙𝚊𝚊𝚜 𝚒𝚝𝚗𝚊 𝚙𝚊𝚒𝚜𝚊 𝚗𝚊𝚑𝚒 𝚑𝚊𝚒!")

    users_collection.update_one({"user_id": target_user.id}, {"$inc": {"balance": -rob_amount}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": rob_amount, "daily_robs": 1}})

    await update.message.reply_text(f"💰 <b>Success!</b> Looted <code>{format_money(rob_amount)}</code> from {html.escape(target_user.first_name)}!", parse_mode=ParseMode.HTML)

# --- ❤️ REVIVE & 🛡️ PROTECT ---
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

async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    if is_protected(user_db):
        expiry = get_active_protection(user_db)
        remaining = expiry - datetime.utcnow()
        return await update.message.reply_text(f"🛡️ 𝙰𝚊𝚙 𝚙𝚎𝚑𝚕𝚎 𝚜𝚎 𝚙𝚛𝚘𝚝𝚎𝚌𝚝𝚎𝚍 𝚑𝚘!\n⏳ 𝚁𝚎𝚖𝚊𝚒𝚗𝚒𝚗𝚐: <code>{remaining.days}d {remaining.seconds // 3600}h</code>")
    
    choice = context.args[0] if context.args else "1d"
    cost = PROTECT_2D_COST if choice == "2d" else PROTECT_1D_COST
    days = 2 if choice == "2d" else 1

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"❌ 𝙽𝚎𝚎𝚍𝚜 {format_money(cost)}.")
    
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": datetime.utcnow() + timedelta(days=days)}, "$inc": {"balance": -cost}})
    await update.message.reply_text(f"🛡️ 𝚂𝚑𝚒𝚎𝚕𝚍 𝙰𝚌𝚝𝚒𝚟𝚊𝚝𝚎𝚍 𝚏𝚘𝚛 {days} 𝚍𝚊𝚢(𝚜)!", parse_mode=ParseMode.HTML)
