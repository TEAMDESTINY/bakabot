# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Fixed Attribute Errors

import html
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import DAILY_BONUS, BONUS_COOLDOWN, TAX_RATE
from baka.utils import (
    ensure_user_exists, format_money, 
    resolve_target, stylize_text
)
from baka.database import users_collection

# --- 💰 BALANCE COMMAND ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        target_db = ensure_user_exists(update.effective_user)

    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    
    msg = (
        f"👤 <b>Name:</b> {html.escape(target_db.get('name', 'User'))}\n"
        f"💰 <b>Total Balance:</b> <code>{format_money(bal)}</code>\n"
        f"🏆 <b>Global Rank:</b> {rank}\n"
        f"❤️ <b>Status:</b> {target_db.get('status', 'alive')}\n"
        f"⚔️ <b>Kills:</b> {target_db.get('kills', 0)}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🏆 MY RANK COMMAND ---
async def my_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = ensure_user_exists(update.effective_user)
    bal = user_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    await update.message.reply_text(f"🏆 <b>Your Global Rank:</b> {rank}", parse_mode=ParseMode.HTML)

# --- 🌍 TOP RICH COMMAND ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = f"🏆 <b>{stylize_text('GLOBAL TOP 10 RICHEST')}</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » <code>{format_money(user.get('balance', 0))}</code>\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- ⚔️ TOP KILL COMMAND ---
async def top_kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    killers = users_collection.find().sort("kills", -1).limit(10)
    msg = "⚔️ <b>GLOBAL TOP 10 KILLERS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    for i, killer in enumerate(killers, 1):
        msg += f"<b>{i}.</b> {html.escape(killer.get('name', 'User'))} » <code>{killer.get('kills', 0)} Kills</code>\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🎁 GIVE COMMAND (10% Tax) ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ <b>Usage:</b> Reply with <code>/give <amount></code>")

    amount = int(context.args[0])
    tax = int(amount * TAX_RATE)
    total = amount + tax
    
    if sender.get('balance', 0) < total:
        return await update.message.reply_text(f"❌ You need {format_money(total)} (including 10% tax).")

    target = update.message.reply_to_message.from_user
    users_collection.update_one({"user_id": sender['user_id']}, {"$inc": {"balance": -total}})
    users_collection.update_one({"user_id": target.id}, {"$inc": {"balance": amount}})
    await update.message.reply_text(f"💸 Sent {format_money(amount)} to {target.first_name}!")

# --- 📅 DAILY BONUS COMMAND (12h Reward) ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_db = ensure_user_exists(user)
    last_claim = user_db.get("last_bonus_claim")
    now = datetime.utcnow()

    if last_claim and (now < last_claim + timedelta(hours=BONUS_COOLDOWN)):
        wait = (last_claim + timedelta(hours=BONUS_COOLDOWN)) - now
        return await update.message.reply_text(f"⏳ Wait <code>{wait.seconds//3600}h {(wait.seconds//60)%60}m</code>")

    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": DAILY_BONUS}, "$set": {"last_bonus_claim": now}})
    await update.message.reply_text(f"🎁 Claimed {format_money(DAILY_BONUS)}!")
