# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - Monospace Font & English Output

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
    KILL_LIMIT_DAILY, ROB_MAX_AMOUNT
)
from baka.utils import (
    ensure_user_exists, resolve_target, format_money, 
    is_protected, get_mention
)
from baka.database import users_collection, groups_collection

# --- 🛠️ HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    if update.effective_chat.type == "private":
        return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("<code>⚠️ FOR REOPEN USE: /open</code>", parse_mode=ParseMode.HTML)
        return False
    return True

# --- 🔪 1. KILL COMMAND ---
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    attacker = update.effective_user
    attacker_db = ensure_user_exists(attacker)
    now = datetime.utcnow()

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_db_raw, err = await resolve_target(update, context)
        if not target_db_raw: 
            return await update.message.reply_text(f"<code>{err or '⚠️ WHO DO YOU WANT TO KILL?'}</code>", parse_mode=ParseMode.HTML)
        target_user = await context.bot.get_chat(target_db_raw['user_id'])

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"<code>🛡️ {target_user.first_name.upper()} IS PROTECTED.</code>", parse_mode=ParseMode.HTML)

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("<code>🎯 TARGET IS ALREADY DEAD.</code>", parse_mode=ParseMode.HTML)

    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_user.id}, {"$set": {"status": "dead", "death_time": now}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1}})

    await update.message.reply_text(
        f"<code>👤 {attacker.first_name.upper()} KILLED {target_user.first_name.upper()}!</code>\n"
        f"<code>💰 EARNED: {format_money(reward)}</code>", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 2. ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("<code>❗ USAGE: REPLY WITH /rob <amount></code>", parse_mode=ParseMode.HTML)

    try:
        amount = int(context.args[0])
        robber = ensure_user_exists(update.effective_user)
        target = ensure_user_exists(update.message.reply_to_message.from_user)

        if target.get('balance', 0) < amount:
            return await update.message.reply_text(
                f"<code>📉 TARGET DOES NOT HAVE ENOUGH MONEY!</code>\n"
                f"<code>ONLY {format_money(target.get('balance', 0))} AVAILABLE.</code>",
                parse_mode=ParseMode.HTML
            )

        users_collection.update_one({"user_id": target['user_id']}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": robber['user_id']}, {"$inc": {"balance": amount}})

        await update.message.reply_text(f"<code>💰 SUCCESS! LOOTED {format_money(amount)}!</code>", parse_mode=ParseMode.HTML)
    except ValueError:
        await update.message.reply_text("<code>❌ ENTER A VALID NUMERIC AMOUNT.</code>", parse_mode=ParseMode.HTML)

# --- ❤️ 3. REVIVE COMMAND (COST: $500) ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if user_db.get('status') == 'alive':
        return await update.message.reply_text("<code>✨ YOU ARE ALREADY ALIVE!</code>", parse_mode=ParseMode.HTML)

    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"<code>❌ REVIVE COSTS: {format_money(REVIVE_COST)}</code>", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": user.id}, {"$set": {"status": "alive"}, "$inc": {"balance": -REVIVE_COST}})
    await update.message.reply_text(f"<code>❤️ REVIVED! FEE: {format_money(REVIVE_COST)} DEDUCTED.</code>", parse_mode=ParseMode.HTML)

# --- 🛡️ 4. PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if not context.args:
        return await update.message.reply_text("<code>⚠️ USAGE: /protect 1d</code>", parse_mode=ParseMode.HTML)

    choice = context.args[0].lower()
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"<code>❌ YOU NEED {format_money(cost)} FOR PROTECTION.</code>", parse_mode=ParseMode.HTML)
    
    expiry = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -cost}})
    await update.message.reply_text("<code>✅ PROTECTION SHIELD ACTIVATED.</code>", parse_mode=ParseMode.HTML)
