# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Daily Reward (24h) & Safe Transactions

import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import TAX_RATE
from baka.utils import (
    ensure_user_exists, format_money, 
    resolve_target, stylize_text
)
from baka.database import users_collection

# --- 💰 BALANCE COMMAND ---
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks wallet balance, rank, and combat stats."""
    target_db, error = await resolve_target(update, context)
    if not target_db: 
        target_db = ensure_user_exists(update.effective_user)

    bal = target_db.get('balance', 0)
    # Calculate rank based on balance
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
    """Quick check for user's global wealth position."""
    user_db = ensure_user_exists(update.effective_user)
    bal = user_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    await update.message.reply_text(f"🏆 <b>Your Global Rank:</b> {rank}", parse_mode=ParseMode.HTML)

# --- 🌍 TOP RICH COMMAND ---
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays top 10 richest players globally."""
    rich_users = users_collection.find().sort("balance", -1).limit(10)
    msg = f"🏆 <b>{stylize_text('GLOBAL TOP 10 RICHEST')}</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    for i, user in enumerate(rich_users, 1):
        msg += f"<b>{i}.</b> {html.escape(user.get('name', 'User'))} » <code>{format_money(user.get('balance', 0))}</code>\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- ⚔️ TOP KILL COMMAND ---
async def top_kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays top 10 deadliest players globally."""
    killers = users_collection.find().sort("kills", -1).limit(10)
    msg = f"⚔️ <b>{stylize_text('GLOBAL TOP 10 KILLERS')}</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    for i, killer in enumerate(killers, 1):
        msg += f"<b>{i}.</b> {html.escape(killer.get('name', 'User'))} » <code>{killer.get('kills', 0)} Kills</code>\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 🎁 GIVE COMMAND (10% Tax) ---
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends money to another user with a 10% transaction tax."""
    sender = ensure_user_exists(update.effective_user)
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("❗ <b>Usage:</b> Reply with <code>/give <amount></code>", parse_mode=ParseMode.HTML)

    if not context.args[0].isdigit():
        return await update.message.reply_text("❌ Please enter a valid number!")

    amount = int(context.args[0])
    
    # Safety Check: Prevent negative/zero amounts
    if amount <= 0:
        return await update.message.reply_text("❌ Amount must be positive!")

    tax = int(amount * TAX_RATE) # 10% tax
    total_deduction = amount + tax
    
    if sender.get('balance', 0) < total_deduction:
        return await update.message.reply_text(f"❌ You need {format_money(total_deduction)} (including 10% tax) to send this.")

    target = update.message.reply_to_message.from_user
    if target.id == sender['user_id']:
        return await update.message.reply_text("🙄 You cannot give money to yourself!")

    # Update database
    users_collection.update_one({"user_id": sender['user_id']}, {"$inc": {"balance": -total_deduction}})
    users_collection.update_one({"user_id": target.id}, {"$inc": {"balance": amount}})
    
    await update.message.reply_text(
        f"💸 <b>Transaction Success!</b>\n"
        f"Sent: <code>{format_money(amount)}</code>\n"
        f"Tax Paid: <code>{format_money(tax)}</code>\n"
        f"Receiver: {html.escape(target.first_name)}",
        parse_mode=ParseMode.HTML
    )

# --- 📅 DAILY BONUS COMMAND (24 HOURS) ---
async def daily_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Gives $1000 every 24 hours. Matches Screenshot exact text.
    """
    user = update.effective_user
    
    # Ensure user exists
    user_db = ensure_user_exists(user)
    
    last_claim = user_db.get("last_daily_claim")
    now = datetime.utcnow()
    
    # Fixed 24 Hour Cooldown
    cooldown_period = timedelta(hours=24)

    # Check Cooldown
    if last_claim:
        time_passed = now - last_claim
        if time_passed < cooldown_period:
            remaining = cooldown_period - time_passed
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            await update.message.reply_text(
                f"⏳ You have already claimed today! Come back in {hours}h {minutes}m."
            )
            return

    # Grant Reward ($1000)
    REWARD = 1000
    users_collection.update_one(
        {"user_id": user.id},
        {
            "$inc": {"balance": REWARD},
            "$set": {"last_daily_claim": now}
        }
    )

    # Exact Text from Screenshot
    msg = (
        f"✅ You received: ${REWARD} daily reward!\n"
        f"💗 Upgrade to premium using /pay to get $2000 daily reward!"
    )
    await update.message.reply_text(msg)
