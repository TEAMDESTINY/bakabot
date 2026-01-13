# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Clean English & Normal Font

import html
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import DAILY_BONUS, REVIVE_COST
from baka.utils import (
    ensure_user_exists,
    format_money,
    resolve_target
)
from baka.database import users_collection, groups_collection

# --- HELPER: ECONOMY STATUS CHECK ---
async def check_economy(update: Update):
    if update.effective_chat.type == ChatType.PRIVATE:
        return True
    group_conf = groups_collection.find_one({"chat_id": update.effective_chat.id})
    if group_conf and not group_conf.get("economy_enabled", True):
        await update.message.reply_text("Economy is disabled. Use /open to enable.")
        return False
    return True

# --- 1. BALANCE (/bal) ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    target_db, _ = await resolve_target(update, context)
    if not target_db:
        target_db = ensure_user_exists(update.effective_user)

    name = html.escape(target_db.get('name', 'User'))
    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    status = target_db.get('status', 'alive')
    kills = target_db.get('kills', 0)

    msg = (
        f"Name: {name}\n"
        f"Balance: {format_money(bal)}\n"
        f"Global Rank: {rank}\n"
        f"Status: {status}\n"
        f"Kills: {kills}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. DAILY BONUS (/daily) ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if update.effective_chat.type != ChatType.PRIVATE:
        bot_username = (await context.bot.get_me()).username
        return await update.message.reply_text(f"Daily Bonus is DM only! t.me/{bot_username}")

    user_db = ensure_user_exists(update.effective_user)
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    if last_claim and (now - last_claim < timedelta(hours=24)):
        wait = timedelta(hours=24) - (now - last_claim)
        hours, rem = divmod(wait.seconds, 3600)
        return await update.message.reply_text(f"Come back in {hours}h.")

    users_collection.update_one({"user_id": update.effective_user.id}, {"$inc": {"balance": DAILY_BONUS}, "$set": {"last_daily_claim": now}})
    await update.message.reply_text(f"You received: ${DAILY_BONUS} daily reward!")

# --- 3. TOP RICH (/toprich) ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = "GLOBAL TOP 10 RICHEST\n" + ("-" * 20) + "\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"{i}. {html.escape(user.get('name', 'User'))} » {format_money(user.get('balance', 0))}\n"
    await update.message.reply_text(msg)

# --- 4. MY RANK (/myrank) ---
async def my_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    user_db = ensure_user_exists(update.effective_user)
    bal = user_db.get("balance", 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    await update.message.reply_text(f"Your Global Rank: {rank}\nBalance: {format_money(bal)}")

# --- 5. GIVE (/give) ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_economy(update): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Usage: Reply with /give <amount>")
    try:
        amount = int(context.args[0])
        sender = ensure_user_exists(update.effective_user)
        receiver = ensure_user_exists(update.message.reply_to_message.from_user)
        if sender["balance"] < amount: return await update.message.reply_text("Insufficient balance.")
        users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -amount}})
        users_collection.update_one({"user_id": receiver["user_id"]}, {"$inc": {"balance": amount}})
        await update.message.reply_text(f"Success! Sent {format_money(amount)} to {receiver['name']}.")
    except ValueError:
        await update.message.reply_text("Please enter a valid amount.")
