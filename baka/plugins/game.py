# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Master Game Plugin - HTML Format (No Tap-to-Copy)

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
        await update.message.reply_text("<b>⚠️ For reopen use: /open</b>", parse_mode=ParseMode.HTML)
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
            return await update.message.reply_text(f"<b>{err or '⚠️ Who do you want to kill?'}</b>", parse_mode=ParseMode.HTML)
        target_user = await context.bot.get_chat(target_db_raw['user_id'])

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if is_protected(target_db) and attacker.id != OWNER_ID:
        return await update.message.reply_text(f"<b>🛡️ {target_user.first_name.upper()} is protected.</b>", parse_mode=ParseMode.HTML)

    if target_db.get('status') == 'dead':
        return await update.message.reply_text("<b>🎯 Target is already dead.</b>", parse_mode=ParseMode.HTML)

    reward = random.randint(100, 200)
    users_collection.update_one({"user_id": target_user.id}, {"$set": {"status": "dead", "death_time": now}})
    users_collection.update_one({"user_id": attacker.id}, {"$inc": {"balance": reward, "kills": 1}})

    await update.message.reply_text(
        f"<b>👤 {attacker.first_name.upper()} killed {target_user.first_name.upper()}!</b>\n"
        f"<b>💰 Earned: {format_money(reward)}</b>", 
        parse_mode=ParseMode.HTML
    )

# --- 💰 2. ROB COMMAND ---
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = update.effective_user
    
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("<b>❗ Usage: Reply with /rob &lt;amount&gt;</b>", parse_mode=ParseMode.HTML)

    try:
        amount = int(context.args[0])
        robber = ensure_user_exists(user)
        target_user = update.message.reply_to_message.from_user
        target_db = ensure_user_exists(target_user)

        if target_db.get('balance', 0) < amount:
            return await update.message.reply_text(
                f"<b>📉 Target doesn't have enough money!</b>\n"
                f"<b>Only {format_money(target_db.get('balance', 0))} available.</b>",
                parse_mode=ParseMode.HTML
            )

        users_collection.update_one({"user_id": target_db['user_id']}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": robber['user_id']}, {"$inc": {"balance": amount}})

        # Success Output
        await update.message.reply_text(
            f"<b>💰 {user.first_name} robbed {target_user.first_name}!</b>\n"
            f"<b>Looted: {format_money(amount)}</b>", 
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        # Error Output
        await update.message.reply_text(
            "<b>❌ Enter a valid numeric amount.</b>", 
            parse_mode=ParseMode.HTML
        )

# --- ❤️ 3. REVIVE COMMAND ---
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_user = user

    target_db = users_collection.find_one({"user_id": target_user.id}) or ensure_user_exists(target_user)
    
    if target_db.get('status') == 'alive':
        return await update.message.reply_text(f"<b>✅ {target_user.first_name} is already alive!</b>", parse_mode=ParseMode.HTML)

    if user_db.get('balance', 0) < REVIVE_COST: 
        return await update.message.reply_text(f"<b>❌ Revive costs: {format_money(REVIVE_COST)}</b>", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": target_user.id}, {"$set": {"status": "alive", "death_time": None}})
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -REVIVE_COST}})
    
    await update.message.reply_text(
        f"<b>❤️ {target_user.first_name} has been revived!</b>\n"
        f"<b>Fee: {format_money(REVIVE_COST)} deducted from {user.first_name}.</b>", 
        parse_mode=ParseMode.HTML
    )

# --- 🛡️ 4. PROTECT COMMAND ---
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user = update.effective_user
    user_db = ensure_user_exists(user)
    
    if not context.args:
        return await update.message.reply_text("<b>⚠️ Usage: /protect 1d</b>", parse_mode=ParseMode.HTML)

    choice = context.args[0].lower()
    cost, days = (PROTECT_2D_COST, 2) if choice == "2d" else (PROTECT_1D_COST, 1)

    if user_db.get('balance', 0) < cost: 
        return await update.message.reply_text(f"<b>❌ You need {format_money(cost)} for protection.</b>", parse_mode=ParseMode.HTML)
    
    expiry = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one({"user_id": user.id}, {"$set": {"protection_expiry": expiry}, "$inc": {"balance": -cost}})
    await update.message.reply_text("<b>🛡️ You are now protected for 1d. </b>", parse_mode=ParseMode.HTML)
